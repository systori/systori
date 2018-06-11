from decimal import Decimal as D
from django.test import TestCase

from systori.lib.accounting.tools import Amount
from systori.lib.testing import make_amount as A

from ..company.factories import CompanyFactory
from ..project.factories import ProjectFactory
from ..task.factories import JobFactory, TaskFactory

from .models import Account, Transaction, Entry, create_account_for_job
from .workflow import debit_jobs, credit_jobs, adjust_jobs, refund_jobs
from .workflow import create_chart_of_accounts
from .constants import (
    SKR03_BANK_CODE,
    SKR03_CASH_DISCOUNT_CODE,
    SKR03_INCOME_CODE,
    SKR03_PARTIAL_PAYMENTS_CODE,
    SKR03_PROMISED_PAYMENTS_CODE,
    SKR03_TAX_PAYMENTS_CODE,
)


class WorkflowTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addTypeEqualityFunc(Amount, "assertAmountEqual")

    def setUp(self):
        self.company = CompanyFactory()
        self.project = ProjectFactory()

        create_chart_of_accounts(self)

        self.job = JobFactory(project=self.project)
        self.job.account = create_account_for_job(self.job)
        self.job.save()
        TaskFactory(qty=10, complete=5, price=96, group=self.job)

        self.job2 = JobFactory(project=self.project)
        self.job2.account = create_account_for_job(self.job2)
        self.job2.save()

    def assertAmountEqual(self, expected, actual, msg):
        self.assertEqual(expected.net, actual.net, "net")
        self.assertEqual(expected.tax, actual.tax, "tax")
        self.assertEqual(expected.gross, actual.gross, "gross")

    def assert_balances(
        self,
        bank=A(),
        balance=A(),
        invoiced=None,
        debited=None,
        paid=None,
        credited=None,
        promised=A(),
        discounts=A(),
        partial=A(),
        income=A(),
        tax=A(),
        switch_to_job=None,
    ):

        if switch_to_job is not None:
            original_job = self.job
            self.job = switch_to_job

        if invoiced and not debited:
            debited = invoiced
        elif not invoiced and debited:
            invoiced = debited
        elif not invoiced and not debited:
            invoiced = A()
            debited = A()

        if paid and not credited:
            credited = paid
        elif not paid and credited:
            paid = credited
        elif not paid and not credited:
            paid = A()
            credited = A()

        self.assertEquals(balance, self.job.account.balance)
        self.assertEquals(invoiced, self.job.account.invoiced)
        self.assertEquals(debited, self.job.account.debits.sum)
        self.assertEquals(paid, self.job.account.paid)
        self.assertEquals(credited, self.job.account.credits.sum)

        self.assertEquals(promised, promised_payments().balance)
        self.assertEquals(partial, partial_payments().balance)
        self.assertEquals(income, income_account().balance)
        self.assertEquals(tax, tax_account().balance)
        self.assertEquals(discounts, discount_account().balance)
        self.assertEquals(bank, bank_account().balance)

        if switch_to_job:
            self.job = original_job


class TestDeletingThings(WorkflowTestCase):
    def setUp(self):
        super().setUp()
        credit_jobs([(self.job, A(100), A(), A())], D(100))

    def test_that_all_entries_are_also_deleted(self):
        self.assertEquals(A(100).negate, self.job.account.balance)
        Transaction.objects.first().delete()
        self.assertEquals(A(), self.job.account.balance)

    def test_delete_account_when_job_is_deleted(self):
        account_id = self.job.account.id
        self.assertTrue(Account.objects.filter(id=account_id).exists())
        self.job.delete()
        self.assertFalse(Account.objects.filter(id=account_id).exists())


class TestCompletedContractAccountingMethod(WorkflowTestCase):
    """ http://accountingexplained.com/financial/revenue/completed-contract-method """

    # Before Revenue Recognition

    def test_before_any_progress_debits(self):
        # everything starts off at 0
        self.assert_balances()

    def test_progress_debit(self):
        debit_jobs([(self.job, A(480), Entry.WORK_DEBIT)])
        self.assert_balances(
            invoiced=A(480), promised=A(480), balance=A(480)
        )  # <- gross we're owed

    def test_payment(self):
        """ Best case is when payment matches debit. """
        debit_jobs([(self.job, A(480), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, A(480), A(0), A(0))], D(480))
        self.assert_balances(
            bank=A(480, 0, 0),
            invoiced=A(480),
            paid=A(-480),
            partial=A(480).net_amount,
            tax=A(480).tax_amount,
        )

    def test_overpayment(self):
        """ Customer pays more than was debited causing negative account balance. """
        debit_jobs([(self.job, A(500), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, A(580), A(0), A(0))], D(580))
        diff = A(500) - A(580)
        self.assert_balances(
            bank=A(580, 0, 0),
            invoiced=A(500),
            paid=A(-580),
            partial=A(580).net_amount,
            tax=A(580).tax_amount,
            balance=diff,
            promised=diff,
        )  # <- negative balances because of overpayment

    def test_underpayment(self):
        """ Customer pays less than was debited without any discounts or adjustments applied. """
        debit_jobs([(self.job, A(500), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, A(480), A(0), A(0))], D(480))
        diff = A(500) - A(480)
        self.assert_balances(
            bank=A(480, 0, 0),
            invoiced=A(500),
            paid=A(-480),
            partial=A(480).net_amount,
            tax=A(480).tax_amount,
            balance=diff,
            promised=diff,
        )  # <- negative balances because of overpayment

    def test_adjusted_payment_matching_invoice(self):
        """ Payment entered along with an adjustment to exactly match the debit. """
        debit_jobs([(self.job, A(500), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, A(480), A(0), A(20))], D(480))
        self.assert_balances(
            bank=A(480, 0, 0),
            debited=A(500),
            invoiced=A(480),  # debited (500) + adjustment (-20) = invoiced (480)
            paid=A(-480),
            credited=A(-500),  # payment (-480) + adjustment (-20) = credited (-500)
            partial=A(480).net_amount,
            tax=A(480).tax_amount,
        )

    def test_adjusted_payment_still_below_invoice(self):
        """ Payment entered along with an adjustment but still not enough to cover the debit. """
        debit_jobs([(self.job, A(600), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, A(480), A(0), A(20))], D(480))
        self.assert_balances(
            bank=A(480, 0, 0),
            balance=A(100),  # debited (600) + credited (-500) = balance (100)
            debited=A(600),
            invoiced=A(580),  # debited (600) + adjustment (-20) = invoiced (580)
            paid=A(-480),
            credited=A(-500),  # payment (-480) + adjustment (-20) = credited (-500)
            promised=A(100),
            partial=A(480).net_amount,
            tax=A(480).tax_amount,
        )

    def test_adjustment_only(self):
        """ Only adjustment entered. """
        debit_jobs([(self.job, A(600), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, A(0), A(0), A(400))], D(0))
        self.assert_balances(
            bank=A(0),
            balance=A(200),  # debited (600) + credited (-400) = balance (200)
            debited=A(600),
            invoiced=A(200),  # debited (600) + adjustment (-400) = invoiced (200)
            paid=A(0),
            credited=A(-400),  # payment (0) + adjustment (-400) = credited (-400)
            promised=A(200),
            partial=A(0),
            tax=A(0),
        )

    def test_discounted_payment_matching_debit(self):
        """ Payment entered along with a discount to exactly match the debit. """
        debit_jobs([(self.job, A(500), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, A(480), A(20), A(0))], D(480))
        self.assert_balances(
            bank=A(480, 0, 0),
            debited=A(500),
            invoiced=A(500),  # debited (500) + adjustment (0) = invoiced (500)
            paid=A(-500),
            credited=A(-500),  # payment (-500) + adjustment (0) = credited (-500)
            partial=A(480).net_amount,
            tax=A(480).tax_amount,
        )

    def test_discounted_payment_below_debit(self):
        """ Payment entered along with a discount but still not enough to cover the debit. """
        debit_jobs([(self.job, A(600), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, A(480), A(20), A(0))], D(480))
        self.assert_balances(
            bank=A(480, 0, 0),
            balance=A(100),  # debited (600) + credited (-500) = balance (100)
            debited=A(600),
            invoiced=A(600),  # debited (600) + adjustment (0) = invoiced (600)
            paid=A(-500),
            credited=A(-500),  # payment (-500) + adjustment (0) = credited (-500)
            promised=A(100),
            partial=A(480).net_amount,
            tax=A(480).tax_amount,
        )

    def test_split_payment_with_discount_and_adjustment(self):
        """ Split payment where one job is discounted and another is adjusted. """
        debit_jobs(
            [
                (self.job, A(480), Entry.FLAT_DEBIT),
                (self.job2, A(480), Entry.WORK_DEBIT),
            ]
        )
        self.assertEquals(A(480), self.job2.account.balance)
        self.assert_balances(promised=A(960), balance=A(480), invoiced=A(480))
        credit_jobs(
            [
                (self.job, A(440), A(0), A(40)),  # adjusted
                (self.job2, A(460), A(20), A(0)),  # discounted
            ],
            D(900),
        )
        self.assert_balances(
            bank=A(900, 0, 0),
            debited=A(480),
            invoiced=A(440),  # debited (480) + adjustment (-40) = invoiced (440)
            paid=A(-440),
            credited=A(-480),  # payment (-440) + adjustment (-40) = credited (-480)
            partial=A(900).net_amount,
            tax=A(900).tax_amount,
        )
        self.assert_balances(
            bank=A(900, 0, 0),
            debited=A(480),
            invoiced=A(480),  # debited (480) + adjustment (0) = invoiced (480)
            paid=A(-480),
            credited=A(-480),  # payment (-480) + adjustment (0) = credited (-480)
            partial=A(900).net_amount,
            tax=A(900).tax_amount,
            switch_to_job=self.job2,
        )

    def test_adjust_with_adjustment(self):
        """ Only adjustment requested. """
        debit_jobs([(self.job, A(600), Entry.WORK_DEBIT)])
        adjust_jobs([(self.job, A(-400))])
        self.assert_balances(
            bank=A(0),
            balance=A(200),  # debited (600) + credited (-400) = balance (200)
            debited=A(600),
            invoiced=A(200),  # debited (600) + adjustment (-400) = invoiced (200)
            paid=A(0),
            credited=A(-400),  # payment (0) + adjustment (-400) = credited (-400)
            promised=A(200),
            partial=A(0),
            tax=A(0),
        )

    def test_refund_with_bank_refund(self):
        """ Customer overpaid an invoice, so we need to refund some cash. """
        debit_jobs([(self.job, A(600), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, A(650), A(0), A(0))], D(650))
        refund_jobs([(self.job, A(50), A(0))])
        self.assert_balances(
            bank=A(600, 0, 0),
            balance=A(0),
            promised=A(0),
            debited=A(
                650
            ),  # invoice debit (600) + refund debit (50) = total debited (650)
            invoiced=A(600),  # invoice debit (600) = total invoiced (600)
            paid=A(-600),  # payment credit (-650) + refund (50) = paid (-600)
            credited=A(
                -650
            ),  # payment credit (-650) + adjustment (0) = credited (-650)
            partial=A(600).net_amount,
            tax=A(600).tax_amount,
        )

    def test_refund_with_applied_refund(self):
        """ Customer pays the correct amount but it is incorrectly applied to jobs.
            Issue a partial refund to first job and immediately apply that to the second job.
        """
        # Invoice 700.00
        debit_jobs(
            [(self.job, A(680), Entry.WORK_DEBIT), (self.job2, A(20), Entry.WORK_DEBIT)]
        )

        # Payment of 700.00 is incorrectly applied to first job
        credit_jobs([(self.job, A(700), A(0), A(0))], D(700))

        self.assert_balances(
            bank=A(700, 0, 0),
            balance=A(-20),
            promised=A(0),
            debited=A(
                680
            ),  # invoice debit (680) + refund debit (0) = total debited (680)
            invoiced=A(
                680
            ),  # invoice debit (680) + adjustment (0) = total invoiced (680)
            paid=A(-700),  # payment credit (-700) + refund debit (0) = paid (-700)
            credited=A(
                -700
            ),  # payment credit (-700) + adjustment (0) = total credited (-700)
            partial=A(700).net_amount,
            tax=A(700).tax_amount,
        )

        self.assert_balances(
            bank=A(700, 0, 0),
            balance=A(20),
            promised=A(0),
            debited=A(20),  # invoice debit (20) + refund debit (0) = total debited (20)
            invoiced=A(20),  # invoice debit (20) + adjustment (0) = total invoiced (20)
            paid=A(0),  # payment credit (0) + refund debit (0) = paid (0)
            credited=A(0),  # payment credit (0) + adjustment (0) = total credited (0)
            partial=A(700).net_amount,
            tax=A(700).tax_amount,
            switch_to_job=self.job2,
        )

        # Refund 20.00 from first job and apply to second job
        refund_jobs([(self.job, A(20), A(0)), (self.job2, A(0), A(20))])

        self.assert_balances(
            bank=A(700, 0, 0),
            balance=A(0),
            promised=A(0),
            debited=A(
                700
            ),  # invoice debit (680) + refund debit (20) = total debited (700)
            invoiced=A(
                680
            ),  # invoice debit (680) + adjustment (0) = total invoiced (680)
            paid=A(-680),  # payment credit (-700) + refund debit (20) = paid (-680)
            credited=A(
                -700
            ),  # payment credit (-700) + adjustment (0) = total credited (-700)
            partial=A(700).net_amount,
            tax=A(700).tax_amount,
        )

        self.assert_balances(
            bank=A(700, 0, 0),
            balance=A(0),
            promised=A(0),
            debited=A(
                20
            ),  # invoice debit (20) + refund debit (20) = total debited (70)
            invoiced=A(20),  # invoice debit (20) + adjustment (0) = total invoiced (20)
            paid=A(-20),  # payment credit (-20) + refund debit (0) = paid (-20)
            credited=A(
                -20
            ),  # payment credit (-20) + adjustment (0) = total credited (-20)
            partial=A(700).net_amount,
            tax=A(700).tax_amount,
            switch_to_job=self.job2,
        )

    def test_refund_with_applied_refund_and_bank_refund(self):
        """ Customer overpays invoice and the overpayment is further incorrectly applied.
            Issue a partial refund to first job, apply that to the second job, refund to customer the rest.
        """
        # Invoice 600.00
        debit_jobs(
            [(self.job, A(580), Entry.WORK_DEBIT), (self.job2, A(20), Entry.WORK_DEBIT)]
        )

        # Payment of 700.00 is incorrectly applied to first job
        credit_jobs([(self.job, A(700), A(0), A(0))], D(700))

        one = A(n="-0.01", t="0.01")

        self.assert_balances(
            bank=A(700, 0, 0),
            balance=A("-120") + one,
            promised=A(-100) + one,
            debited=A(
                580
            ),  # invoice debit (680) + refund debit (0) = total debited (680)
            invoiced=A(
                580
            ),  # invoice debit (680) + adjustment (0) = total invoiced (680)
            paid=A(-700),  # payment credit (-700) + refund debit (0) = paid (-700)
            credited=A(
                -700
            ),  # payment credit (-700) + adjustment (0) = total credited (-700)
            partial=A(700).net_amount,
            tax=A(700).tax_amount,
        )

        self.assert_balances(
            bank=A(700, 0, 0),
            balance=A(20),
            promised=A(-100) + one,
            debited=A(20),  # invoice debit (20) + refund debit (0) = total debited (20)
            invoiced=A(20),  # invoice debit (20) + adjustment (0) = total invoiced (20)
            paid=A(0),  # payment credit (0) + refund debit (0) = paid (0)
            credited=A(0),  # payment credit (0) + adjustment (0) = total credited (0)
            partial=A(700).net_amount,
            tax=A(700).tax_amount,
            switch_to_job=self.job2,
        )

        # Refund 20.00 from first job and apply to second job
        refund_jobs([(self.job, A(120) - one, A(0)), (self.job2, A(0), A(20))])

        self.assert_balances(
            bank=A(600, 0, 0),
            balance=A(0),
            promised=A(0),
            debited=A(
                700
            ),  # invoice debit (680) + refund debit (20) = total debited (700)
            invoiced=A(
                580
            ),  # invoice debit (680) + adjustment (0) = total invoiced (680)
            paid=A(-580),  # payment credit (-700) + refund debit (20) = paid (-680)
            credited=A(
                -700
            ),  # payment credit (-700) + adjustment (0) = total credited (-700)
            partial=A(600).net_amount,
            tax=A(600).tax_amount,
        )

        self.assert_balances(
            bank=A(600, 0, 0),
            balance=A(0),
            promised=A(0),
            debited=A(
                20
            ),  # invoice debit (20) + refund debit (20) = total debited (70)
            invoiced=A(20),  # invoice debit (20) + adjustment (0) = total invoiced (20)
            paid=A(-20),  # payment credit (-20) + refund debit (0) = paid (-20)
            credited=A(
                -20
            ),  # payment credit (-20) + adjustment (0) = total credited (-20)
            partial=A(600).net_amount,
            tax=A(600).tax_amount,
            switch_to_job=self.job2,
        )

    # After Revenue Recognition

    def test_revenue_debits(self):
        """ Enter a debit and enable revenue recognition, then perform another debit but this time
            without explicit revenue recognition since job already knows it's in revenue recognition mode.
        """
        debit_jobs([(self.job, A(480), Entry.WORK_DEBIT)], recognize_revenue=True)
        self.assert_balances(
            balance=A(480),
            invoiced=A(480),
            income=A(480).net_amount,
            tax=A(480).tax_amount,
        )
        debit_jobs(
            [(self.job, A(480), Entry.WORK_DEBIT)]
        )  # this job is already in revenue recognition mode
        self.assert_balances(
            balance=A(960),
            invoiced=A(960),
            income=A(960).net_amount,
            tax=A(960).tax_amount,
        )  # <- gross we're owed

    def test_previous_revenue_gets_recognized(self):
        """ Create a debit and an underpayment then transition this job into revenue recognition mode
            without actually entering any new work debits. This should move all previously promised and
            cash revenues into the main income account.
        """
        debit_jobs([(self.job, A(480), Entry.FLAT_DEBIT)])  # some promised revenue
        credit_jobs([(self.job, A(200), A(0), A(0))], D(200))  # some cash revenue
        self.assert_balances(
            bank=A(200, 0, 0),
            balance=A(280),
            invoiced=A(480),
            paid=A(-200),
            partial=A(200).net_amount,
            tax=A(200).tax_amount,
            promised=A(280),
        )

        # trick debit_jobs() into running a zero debit in order to transition job to recognized revenue mode
        debit_jobs([(self.job, A(0), Entry.FLAT_DEBIT)], recognize_revenue=True)

        # income now includes the previous promised revenue and cash revenue
        self.assert_balances(
            bank=A(200, 0, 0),
            balance=A(280),
            invoiced=A(480),
            paid=A(-200),
            debited=A(480)
            + A(280),  # invoice debit (480) + reset debit (280) = total debits (760)
            credited=A(
                -480
            ),  # payment credit (-200) + unpaid balance (-280) = total credits (-480)
            income=A(480).net_amount,
            tax=A(480).tax_amount,
        )

    def test_overpayment_then_new_debit_with_recognized_revenue(self):
        """ Create a debit transitioning this job into revenue recognition mode then
            enter an overpayment. This tests that the extra portion of the overpayment
            is not taxed and that it takes another debit equaling the overpaid amount
            to get all taxes and income properly recognized.
        """
        debit_jobs([(self.job, A(480), Entry.FLAT_DEBIT)], recognize_revenue=True)
        credit_jobs([(self.job, A(960), A(0), A(0))], D(960))
        self.assert_balances(
            bank=A(960, 0, 0),
            balance=A(-480),
            invoiced=A(480),
            paid=A(-960),
            income=A(480).net_amount,
            tax=A(480).tax_amount,
        )
        debit_jobs([(self.job, A(480), Entry.FLAT_DEBIT)])
        self.assert_balances(
            bank=A(960, 0, 0),
            invoiced=A(960),
            paid=A(-960),
            income=A(960).net_amount,
            tax=A(960).tax_amount,
        )

    def test_adjusted_payment_matching_debit_with_recognized_revenue(self):
        """ Payment entered to revenue recognized account along with an adjustment
            to exactly match the debit.
        """
        debit_jobs([(self.job, A(500), Entry.WORK_DEBIT)], recognize_revenue=True)
        credit_jobs([(self.job, A(480), A(0), A(20))], D(480))
        self.assert_balances(
            bank=A(480, 0, 0),
            invoiced=A(480),
            paid=A(-480),
            debited=A(500),
            credited=A(-500),
            income=A(480).net_amount,
            tax=A(480).tax_amount,
        )

    def test_adjusted_payment_below_debit_with_recognized_revenue(self):
        """ Payment entered to revenue recognized account along with an adjustment
            but still not enough to cover the debit.
        """
        debit_jobs([(self.job, A(600), Entry.WORK_DEBIT)], recognize_revenue=True)
        credit_jobs([(self.job, A(480), A(0), A(20))], D(480))
        self.assert_balances(
            bank=A(480, 0, 0),
            balance=A(100),  # <- job still has some balance
            invoiced=A(580),
            paid=A(-480),  # <- 20.00 adjusted
            debited=A(600),
            credited=A(-500),
            income=A(580).net_amount,
            tax=A(580).tax_amount,
        )  # <- income is higher than bank balance

    def test_discounted_payment_matching_debit_with_recognized_revenue(self):
        """ Payment entered to revenue recognized account along with a cash discount
            to exactly match the debit.
        """
        debit_jobs([(self.job, A(500), Entry.WORK_DEBIT)], recognize_revenue=True)
        credit_jobs([(self.job, A(480), A(20), A(0))], D(480))
        self.assert_balances(
            bank=A(480, 0, 0),
            invoiced=A(500),
            paid=A(-500),
            income=A(500).net_amount,
            tax=A(480).tax_amount,
            discounts=A(-20).net_amount,
        )

    def test_discounted_payment_below_debit_with_recognized_revenue(self):
        """ Payment entered to revenue recognized account along with a cash discount
            but still not enough to cover the debit.
        """
        debit_jobs([(self.job, A(600), Entry.WORK_DEBIT)], recognize_revenue=True)
        credit_jobs([(self.job, A(480), A(20), A(0))], D(480))
        self.assert_balances(
            bank=A(480, 0, 0),
            balance=A(100),
            invoiced=A(600),
            paid=A(-500),
            income=A(600).net_amount,
            tax=A(580).tax_amount,
            discounts=A(-20).net_amount,
        )

    def test_happy_path_scenario(self):
        """ Tests the simple job life cycle from progress invoice to final payment.
        """
        debit_jobs([(self.job, A(480), Entry.FLAT_DEBIT)])  # progress invoice
        credit_jobs([(self.job, A(100), A(0), A(0))], D(100))  # progress payment
        debit_jobs(
            [(self.job, A(480), Entry.FLAT_DEBIT)], recognize_revenue=True
        )  # final invoice
        credit_jobs([(self.job, A(800), A(60), A(0))], D(800))  # final payment

        self.assert_balances(
            bank=A(900, 0, 0),
            invoiced=A(960),
            paid=A(-960),
            debited=A(480 * 2 + 380),
            credited=A(-480 * 2 - 380),
            income=A(960).net_amount,
            tax=A(900).tax_amount,
            discounts=A(-60).net_amount,
        )

        total_income = income_account().balance + discount_account().balance
        self.assertEqual(total_income, A(900).net_amount)

    def test_refund_with_applied_refund_and_bank_refund_and_recognized_revenue(self):
        """ Customer overpays final invoice and the overpayment is further incorrectly applied.
            Issue a partial refund to first job, apply that to the second job, refund to customer the rest.
        """

        # Invoice 600.00
        debit_jobs(
            [
                (self.job, A(580), Entry.WORK_DEBIT),
                (self.job2, A(20), Entry.WORK_DEBIT),
            ],
            recognize_revenue=True,
        )

        # Payment of 700.00 is incorrectly applied to first job
        credit_jobs([(self.job, A(700), A(0), A(0))], D(700))

        one = A(n="-0.01", t="0.01")

        self.assert_balances(
            bank=A(700, 0, 0),
            balance=A("-120") + one,
            debited=A(
                580
            ),  # invoice debit (680) + refund debit (0) = total debited (680)
            invoiced=A(
                580
            ),  # invoice debit (680) + adjustment (0) = total invoiced (680)
            paid=A(-700),  # payment credit (-700) + refund debit (0) = paid (-700)
            credited=A(
                -700
            ),  # payment credit (-700) + adjustment (0) = total credited (-700)
            income=A(600).net_amount,
            tax=A(600).tax_amount,
        )

        self.assert_balances(
            bank=A(700, 0, 0),
            balance=A(20),
            debited=A(20),  # invoice debit (20) + refund debit (0) = total debited (20)
            invoiced=A(20),  # invoice debit (20) + adjustment (0) = total invoiced (20)
            paid=A(0),  # payment credit (0) + refund debit (0) = paid (0)
            credited=A(0),  # payment credit (0) + adjustment (0) = total credited (0)
            income=A(600).net_amount,
            tax=A(600).tax_amount,
            switch_to_job=self.job2,
        )

        # Refund 20.00 from first job and apply to second job
        refund_jobs([(self.job, A(120) - one, A(0)), (self.job2, A(0), A(20))])

        self.assert_balances(
            bank=A(600, 0, 0),
            balance=A(0),
            debited=A(
                700
            ),  # invoice debit (680) + refund debit (20) = total debited (700)
            invoiced=A(
                580
            ),  # invoice debit (680) + adjustment (0) = total invoiced (680)
            paid=A(-580),  # payment credit (-700) + refund debit (20) = paid (-680)
            credited=A(
                -700
            ),  # payment credit (-700) + adjustment (0) = total credited (-700)
            income=A(600).net_amount,
            tax=A(600).tax_amount,
        )

        self.assert_balances(
            bank=A(600, 0, 0),
            balance=A(0),
            debited=A(
                20
            ),  # invoice debit (20) + refund debit (20) = total debited (70)
            invoiced=A(20),  # invoice debit (20) + adjustment (0) = total invoiced (20)
            paid=A(-20),  # payment credit (-20) + refund debit (0) = paid (-20)
            credited=A(
                -20
            ),  # payment credit (-20) + adjustment (0) = total credited (-20)
            income=A(600).net_amount,
            tax=A(600).tax_amount,
            switch_to_job=self.job2,
        )


class TestRevenueRecognitionEdgeCases(WorkflowTestCase):
    """ The revenue recognition algorithm needs to handle situations
        where the net/tax on the balance are actually different signs or zero/non-zero,
        we test four cases:
         Case 1. net:  0.00, tax:  0.01
         Case 2. net:  0.01, tax:  0.00
         Case 3. net: -0.01, tax:  0.01 (requires additional debit: net: 0.01, tax: 0.00)
         Case 4. net:  0.01, tax: -0.01 (requires additional debit: net: 0.00, tax: 0.01)
    """

    def test_case1(self):
        self.caseA_test(A(n="0.00", t="0.01"))

    def test_case2(self):
        self.caseA_test(A(n="0.01", t="0.00"))

    def caseA_test(self, case):
        """ Covers the case where either net or tax are zero but the other part is greater than zero.
        """
        debit_jobs([(self.job, case, Entry.FLAT_DEBIT)])
        self.assert_balances(balance=case, invoiced=case, promised=case)
        debit_jobs([(self.job, A(0), Entry.FLAT_DEBIT)], recognize_revenue=True)
        self.assert_balances(
            balance=case,
            invoiced=case,
            credited=case.negate,  # the recognized revenue debit first clears the oustanding balance
            debited=case
            + case,  # the recognized revenue debit then re-debits the outstanding balance
            paid=A(
                0
            ),  # there is income due to revenue recognition, but nothing actually paid yet
            income=case.net_amount,
            tax=case.tax_amount,
        )

    def test_case3(self):
        self.caseB_test(A(n="0.01"), A(t="0.01"))

    def test_case4(self):
        self.caseB_test(A(t="0.01"), A(n="0.01"))

    def caseB_test(self, payment, debit):
        """ Covers the case where one part is negative and the other is positive.
            Because it's not actually possible to end up with a negative net or tax on
            on the invoice (don't want negative invoice) we have to zero-out the negative
            part in the final debit.
        """
        credit_jobs(
            [(self.job, payment, A(0), A(0))], payment.gross
        )  # this creates the 'negative' part of balance
        debit_jobs(
            [(self.job, debit, Entry.FLAT_DEBIT)]
        )  # this creates the 'positive' part of balance
        case = (
            payment.negate + debit
        )  # this is either net:-0.01,tax:0.01 or net:0.01,tax:-0.01
        self.assert_balances(
            bank=A(payment.gross, 0, 0),
            balance=case,
            invoiced=debit,
            promised=case,
            partial=payment.net_amount,
            tax=payment.tax_amount,
            paid=payment.negate,
        )
        zero_out_payment = A(
            n=payment.net, t=payment.tax
        )  # we can't create final invoice with negative net/tax
        debit_jobs(
            [(self.job, zero_out_payment, Entry.FLAT_DEBIT)], recognize_revenue=True
        )
        self.assert_balances(
            bank=A(payment.gross, 0, 0),
            balance=debit,
            invoiced=payment + debit,
            credited=A(
                n="0.01", t="0.01"
            ).negate,  # the recognized revenue debit first clears the oustanding balance
            debited=debit
            + debit
            + zero_out_payment,  # the recognized revenue debit then re-debits the outstanding balance
            paid=payment.negate,
            income=A(n="0.01"),
            tax=A(t="0.01"),
        )


def promised_payments():
    return Account.objects.get(code=SKR03_PROMISED_PAYMENTS_CODE)


def partial_payments():
    return Account.objects.get(code=SKR03_PARTIAL_PAYMENTS_CODE)


def income_account():
    return Account.objects.get(code=SKR03_INCOME_CODE)


def tax_account():
    return Account.objects.get(code=SKR03_TAX_PAYMENTS_CODE)


def discount_account():
    return Account.objects.get(code=SKR03_CASH_DISCOUNT_CODE)


def bank_account():
    return Account.objects.get(code=SKR03_BANK_CODE)
