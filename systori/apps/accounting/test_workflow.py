from decimal import Decimal as D
from django.test import TestCase
from unittest import skip
from systori.lib.accounting.tools import Amount, extract_net_tax
from ..task.test_models import create_task_data
from .models import Account, Transaction, Entry, create_account_for_job
from .workflow import create_chart_of_accounts
from .workflow import debit_jobs, credit_jobs, adjust_jobs
from .constants import *


def A(g=None, n=None, t=None):
    if g and n == 0 and t == 0:
        return Amount(D(0), D(0), D(g))
    if g:
        return Amount.from_gross(D(g), TAX_RATE)
    if n and not t:
        return Amount(D(n), D(0))
    if not n and t:
        return Amount(D(0), D(t))
    if n and t:
        return Amount(D(n), D(t))
    return Amount.zero()


class AccountingTestCase(TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addTypeEqualityFunc(Amount, 'assertAmountEqual')

    def assertAmountEqual(self, expected, actual, msg):
        self.assertEqual(expected.gross, actual.gross, 'gross')
        self.assertEqual(expected.net, actual.net, 'net')
        self.assertEqual(expected.tax, actual.tax, 'tax')


def create_data(self):
    create_task_data(self)
    create_chart_of_accounts(self)
    self.job.account = create_account_for_job(self.job)
    self.job.save()
    self.job2.account = create_account_for_job(self.job2)
    self.job2.save()


class TestDeletingThings(AccountingTestCase):
    def setUp(self):
        create_data(self)
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


class TestCompletedContractAccountingMethod(AccountingTestCase):
    """ http://accountingexplained.com/financial/revenue/completed-contract-method """

    def setUp(self):
        create_data(self)

    def assert_balances(self, bank=A(), balance=A(),
                        invoiced=None, debited=None,
                        paid=None, credited=None,
                        promised=A(), discounts=A(),
                        partial=A(), income=A(), tax=A(),
                        switch_to_job=None):

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

    # Before Revenue Recognition

    def test_before_any_progress_debits(self):
        # everything starts off at 0
        self.assert_balances()

    def test_progress_debit(self):
        debit_jobs([(self.job, A(480), Entry.WORK_DEBIT)])
        self.assert_balances(invoiced=A(480), promised=A(480), balance=A(480))  # <- gross we're owed

    def test_payment(self):
        """ Best case is when payment matches debit. """
        debit_jobs([(self.job, A(480), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, A(480), A(0), A(0))], D(480))
        self.assert_balances(bank=A(480, 0, 0), invoiced=A(480), paid=A(-480),
                             partial=A(480).net_amount, tax=A(480).tax_amount)

    def test_overpayment(self):
        """ Customer pays more than was debited causing negative account balance. """
        debit_jobs([(self.job, A(500), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, A(580), A(0), A(0))], D(580))
        diff = A(500) - A(580)
        self.assert_balances(bank=A(580, 0, 0), invoiced=A(500), paid=A(-580),
                             partial=A(580).net_amount, tax=A(580).tax_amount,
                             balance=diff, promised=diff)  # <- negative balances because of overpayment

    def test_underpayment(self):
        """ Customer pays less than was debited without any discounts or adjustments applied. """
        debit_jobs([(self.job, A(500), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, A(480), A(0), A(0))], D(480))
        diff = A(500) - A(480)
        self.assert_balances(bank=A(480, 0, 0), invoiced=A(500), paid=A(-480),
                             partial=A(480).net_amount, tax=A(480).tax_amount,
                             balance=diff, promised=diff)  # <- negative balances because of overpayment

    def test_adjusted_payment_matching_invoice(self):
        """ Payment entered along with an adjustment to exactly match the debit. """
        debit_jobs([(self.job, A(500), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, A(480), A(0), A(20))], D(480))
        self.assert_balances(bank=A(480, 0, 0),
                             debited=A(500), invoiced=A(480),  # debited (500) + adjustment (-20) = invoiced (480)
                             paid=A(-480), credited=A(-500),  # payment (-480) + adjustment (-20) = credited (-500)
                             partial=A(480).net_amount, tax=A(480).tax_amount)

    def test_adjusted_payment_still_below_invoice(self):
        """ Payment entered along with an adjustment but still not enough to cover the debit. """
        debit_jobs([(self.job, A(600), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, A(480), A(0), A(20))], D(480))
        self.assert_balances(bank=A(480, 0, 0), balance=A(100),  # debited (600) + credited (-500) = balance (100)
                             debited=A(600), invoiced=A(580),   # debited (600) + adjustment (-20) = invoiced (580)
                             paid=A(-480), credited=A(-500),   # payment (-480) + adjustment (-20) = credited (-500)
                             promised=A(100), partial=A(480).net_amount, tax=A(480).tax_amount)

    def test_adjustment_only(self):
        """ Only adjustment entered. """
        debit_jobs([(self.job, A(600), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, A(0), A(0), A(400))], D(0))
        self.assert_balances(bank=A(0), balance=A(200),          # debited (600) + credited (-400) = balance (200)
                             debited=A(600), invoiced=A(200),  # debited (600) + adjustment (-400) = invoiced (200)
                             paid=A(0), credited=A(-400),        # payment (0) + adjustment (-400) = credited (-400)
                             promised=A(200), partial=A(0), tax=A(0))

    def test_discounted_payment_matching_debit(self):
        """ Payment entered along with a discount to exactly match the debit. """
        debit_jobs([(self.job, A(500), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, A(480), A(20), A(0))], D(480))
        self.assert_balances(bank=A(480, 0, 0),
                             debited=A(500), invoiced=A(500),  # debited (500) + adjustment (0) = invoiced (500)
                             paid=A(-500), credited=A(-500),  # payment (-500) + adjustment (0) = credited (-500)
                             partial=A(480).net_amount, tax=A(480).tax_amount)

    def test_discounted_payment_below_debit(self):
        """ Payment entered along with a discount but still not enough to cover the debit. """
        debit_jobs([(self.job, A(600), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, A(480), A(20), A(0))], D(480))
        self.assert_balances(bank=A(480, 0, 0), balance=A(100),  # debited (600) + credited (-500) = balance (100)
                             debited=A(600), invoiced=A(600),   # debited (600) + adjustment (0) = invoiced (600)
                             paid=A(-500), credited=A(-500),   # payment (-500) + adjustment (0) = credited (-500)
                             promised=A(100), partial=A(480).net_amount, tax=A(480).tax_amount)

    def test_split_payment_with_discount_and_adjustment(self):
        """ Split payment where one job is discounted and another is adjusted. """
        debit_jobs([
            (self.job, A(480), Entry.FLAT_DEBIT),
            (self.job2, A(480), Entry.WORK_DEBIT)
        ])
        self.assertEquals(A(480), self.job2.account.balance)
        self.assert_balances(promised=A(960), balance=A(480), invoiced=A(480))
        credit_jobs([
            (self.job, A(440), A(0), A(40)),  # adjusted
            (self.job2, A(460), A(20), A(0)),  # discounted
        ], D(900))
        self.assert_balances(bank=A(900, 0, 0),
                             debited=A(480), invoiced=A(440),  # debited (480) + adjustment (-40) = invoiced (440)
                             paid=A(-440), credited=A(-480),  # payment (-440) + adjustment (-40) = credited (-480)
                             partial=A(900).net_amount, tax=A(900).tax_amount)
        self.assert_balances(bank=A(900, 0, 0),
                             debited=A(480), invoiced=A(480),  # debited (480) + adjustment (0) = invoiced (480)
                             paid=A(-480), credited=A(-480),  # payment (-480) + adjustment (0) = credited (-480)
                             partial=A(900).net_amount, tax=A(900).tax_amount,
                             switch_to_job=self.job2)

    def test_adjust_with_adjustment(self):
        """ Only adjustment requested. """
        debit_jobs([(self.job, A(600), Entry.WORK_DEBIT)])
        adjust_jobs([(self.job, A(-400))])
        self.assert_balances(bank=A(0), balance=A(200),          # debited (600) + credited (-400) = balance (200)
                             debited=A(600), invoiced=A(200),  # debited (600) + adjustment (-400) = invoiced (200)
                             paid=A(0), credited=A(-400),        # payment (0) + adjustment (-400) = credited (-400)
                             promised=A(200), partial=A(0), tax=A(0))

    @skip
    def test_adjust_with_bank_refund(self):
        """ Customer overpaid an invoice, so we need to refund some cash. """
        debit_jobs([(self.job, A(600), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, A(650), A(0), A(0))], D(650))
        adjust_jobs([(self.job, A(0), A(50), A(0))])
        self.assert_balances(bank=A(600, 0, 0), balance=A(0), promised=A(0),
                             debited=A(650),    # invoice debit (600) + refund debit (50) = total debited (650)
                             invoiced=A(600),   # invoice debit (600) = total invoiced (600)
                             paid=A(-600),      # payment credit (-650) + refund (50) = paid (-600)
                             credited=A(-650),  # payment credit (-650) + adjustment (0) = credited (-650)
                             partial=A(600).net_amount, tax=A(600).tax_amount)

    @skip
    def test_adjust_with_adjustment_and_bank_refund(self):
        """ Customer overpaid an already inflated invoice, so we need to adjust invoice and refund some cash. """
        # Invoice 680.00
        debit_jobs([(self.job, A(680), Entry.WORK_DEBIT)])
        # Customer pays 640.00
        credit_jobs([(self.job, A(640), A(0), A(0))], D(640))
        # Pretend now that progress changed and billable is now only 600.00
        # We need to reduce invoiced by 80.00 of which 40.00 is a refund
        # A(40) != A(80)-A(40)  # the net/tax is off by 0.01
        a40 = A(80)-A(40)
        a720 = A(680)+a40
        adjust_jobs([(self.job, A(80), a40, A(0))])
        self.assert_balances(bank=A(600, 0, 0), balance=A(0), promised=A(0),
                             debited=a720,          # invoice debit (680) + refund debit (40) = total debited (720)
                             invoiced=A(600),       # invoice debit (600) = total invoiced (600)
                             paid=A(-600),          # payment credit (-650) + refund (50) = paid (-600)
                             credited=a720.negate,  # payment credit (-640) + adjustment (-80) = total credited (-720)
                             partial=A(600).net_amount, tax=A(600).tax_amount)

    @skip
    def test_adjust_with_adjustment_and_applied_refund(self):
        """ Initially customer underpays an invoice with two jobs on it, then the first job billable is reduced.
            So, we adjust the first job, issues a refund, then apply that refund to the second job.
        """
        # Invoice 700.00
        debit_jobs([
            (self.job, A(680), Entry.WORK_DEBIT),
            (self.job2, A(20), Entry.WORK_DEBIT)
        ])
        # Customer pays 500.00, applied to first job
        credit_jobs([(self.job, A(500), A(0), A(0))], D(500))
        # Progress changed and billable is now only 480.00 for first job
        # We need to adjust first job by 200.00 of which 20.00 is a refund, then apply that to second job
        adjust_jobs([
            (self.job, A(200), A(20), A(0)),
            (self.job2, A(0), A(0), A(20))
        ])

        self.assert_balances(bank=A(500, 0, 0), balance=A(0), promised=A(0),
                             debited=A(700),    # invoice debit (680) + refund debit (20) = total debited (700)
                             invoiced=A(480),   # invoice debit (680) + adjustment (-200) = total invoiced (480)
                             paid=A(-480),      # payment credit (-500) + refund debit (20) = paid (-480)
                             credited=A(-700),  # payment credit (-500) + adjustment (-200) = total credited (-700)
                             partial=A(500).net_amount, tax=A(500).tax_amount)

        self.assert_balances(bank=A(500, 0, 0), invoiced=A(20), paid=A(-20),
                             partial=A(500).net_amount, tax=A(500).tax_amount,
                             switch_to_job=self.job2)

    @skip
    def test_adjust_with_adjustment_bank_refund_and_applied_refund(self):
        """ Initially customer underpays an invoice with two jobs on it, then the first job billable is reduced.
            So, we adjust the first job and issues a refund, then apply that to the second job and cash refund the rest.
        """
        # Invoice 700.00
        debit_jobs([
            (self.job, A(680), Entry.WORK_DEBIT),
            (self.job2, A(20), Entry.WORK_DEBIT)
        ])
        # Customer pays 500.00, applied to first job
        credit_jobs([(self.job, A(500), A(0), A(0))], D(500))
        # Progress changed and billable is now only 400.00 for first job
        # We need to adjust first job by 280.00 of which 100.00 is a refund
        # We apply 20.00 of that refund to job 2 and issue cash refund for 80
        adjust_jobs([
            (self.job, A(280), A(100), A(0)),
            (self.job2, A(0), A(0), A(20))
        ])

        # A(400) != A(680)-A(280)  # the net/tax is off by 0.01
        a400 = A(680)-A(280)
        a420 = a400+A(20)
        self.assert_balances(bank=A(420, 0, 0), balance=A(0), promised=A(0),
                             debited=A(780),    # invoice debit (680) + refund debit (100) = total debited (780)
                             invoiced=a400,     # invoice debit (680) + adjustment (-280) = total invoiced (400)
                             paid=a400.negate,      # payment credit (-500) + refund debit (100) = paid (-400)
                             credited=A(-780),  # payment credit (-500) + adjustment (-280) = total credited (-780)
                             partial=a420.net_amount, tax=a420.tax_amount)

        self.assert_balances(bank=A(420, 0, 0), invoiced=A(20), paid=A(-20),
                             partial=a420.net_amount, tax=a420.tax_amount,
                             switch_to_job=self.job2)

    # After Revenue Recognition

    def test_revenue_debits(self):
        """ Enter a debit and enable revenue recognition, then perform another debit but this time
            without explicit revenue recognition since job already knows it's in revenue recognition mode.
        """
        debit_jobs([(self.job, A(480), Entry.WORK_DEBIT)], recognize_revenue=True)
        self.assert_balances(balance=A(480), invoiced=A(480), income=A(480).net_amount, tax=A(480).tax_amount)
        debit_jobs([(self.job, A(480), Entry.WORK_DEBIT)])  # this job is already in revenue recognition mode
        self.assert_balances(balance=A(960), invoiced=A(960), income=A(960).net_amount, tax=A(960).tax_amount)  # <- gross we're owed

    def test_previous_revenue_gets_recognized(self):
        """ Create a debit and an underpayment then transition this job into revenue recognition mode
            without actually entering any new work debits. This should move all previously promised and
            cash revenues into the main income account.
        """
        debit_jobs([(self.job, A(480), Entry.FLAT_DEBIT)])  # some promised revenue
        credit_jobs([(self.job, A(200), A(0), A(0))], D(200))  # some cash revenue
        self.assert_balances(bank=A(200, 0, 0), balance=A(280), invoiced=A(480), paid=A(-200),
                             partial=A(200).net_amount, tax=A(200).tax_amount, promised=A(280))

        # trick debit_jobs() into running a zero debit in order to transition job to recognized revenue mode
        debit_jobs([(self.job, A(0), Entry.FLAT_DEBIT)], recognize_revenue=True)

        # income now includes the previous promised revenue and cash revenue
        self.assert_balances(bank=A(200, 0, 0), balance=A(280),
                             invoiced=A(480), paid=A(-200),
                             debited=A(480)+A(280),  # invoice debit (480) + reset debit (280) = total debits (760)
                             credited=A(-480),  # payment credit (-200) + unpaid balance (-280) = total credits (-480)
                             income=A(480).net_amount, tax=A(480).tax_amount)

    def test_overpayment_then_new_debit_with_recognized_revenue(self):
        """ Create a debit transitioning this job into revenue recognition mode then
            enter an overpayment. This tests that the extra portion of the overpayment
            is not taxed and that it takes another debit equaling the overpaid amount
            to get all taxes and income properly recognized.
        """
        debit_jobs([(self.job, A(480), Entry.FLAT_DEBIT)], recognize_revenue=True)
        credit_jobs([(self.job, A(960), A(0), A(0))], D(960))
        self.assert_balances(bank=A(960, 0, 0), balance=A(-480),
                             invoiced=A(480), paid=A(-960),
                             income=A(480).net_amount, tax=A(480).tax_amount)
        debit_jobs([(self.job, A(480), Entry.FLAT_DEBIT)])
        self.assert_balances(bank=A(960, 0, 0),
                             invoiced=A(960), paid=A(-960),
                             income=A(960).net_amount, tax=A(960).tax_amount)

    def test_adjusted_payment_matching_debit_with_recognized_revenue(self):
        """ Payment entered to revenue recognized account along with an adjustment
            to exactly match the debit.
        """
        debit_jobs([(self.job, A(500), Entry.WORK_DEBIT)], recognize_revenue=True)
        credit_jobs([(self.job, A(480), A(0), A(20))], D(480))
        self.assert_balances(bank=A(480, 0, 0),
                             invoiced=A(480), paid=A(-480),
                             debited=A(500), credited=A(-500),
                             income=A(480).net_amount, tax=A(480).tax_amount)

    def test_adjusted_payment_below_debit_with_recognized_revenue(self):
        """ Payment entered to revenue recognized account along with an adjustment
            but still not enough to cover the debit.
        """
        debit_jobs([(self.job, A(600), Entry.WORK_DEBIT)], recognize_revenue=True)
        credit_jobs([(self.job, A(480), A(0), A(20))], D(480))
        self.assert_balances(bank=A(480, 0, 0), balance=A(100),  # <- job still has some balance
                             invoiced=A(580), paid=A(-480),  # <- 20.00 adjusted
                             debited=A(600), credited=A(-500),
                             income=A(580).net_amount, tax=A(580).tax_amount)  # <- income is higher than bank balance

    def test_discounted_payment_matching_debit_with_recognized_revenue(self):
        """ Payment entered to revenue recognized account along with a cash discount
            to exactly match the debit.
        """
        debit_jobs([(self.job, A(500), Entry.WORK_DEBIT)], recognize_revenue=True)
        credit_jobs([(self.job, A(480), A(20), A(0))], D(480))
        self.assert_balances(bank=A(480, 0, 0), invoiced=A(500), paid=A(-500),
                             income=A(500).net_amount, tax=A(480).tax_amount,
                             discounts=A(-20).net_amount)

    def test_discounted_payment_below_debit_with_recognized_revenue(self):
        """ Payment entered to revenue recognized account along with a cash discount
            but still not enough to cover the debit.
        """
        debit_jobs([(self.job, A(600), Entry.WORK_DEBIT)], recognize_revenue=True)
        credit_jobs([(self.job, A(480), A(20), A(0))], D(480))
        self.assert_balances(bank=A(480, 0, 0), balance=A(100),
                             invoiced=A(600), paid=A(-500),
                             income=A(600).net_amount, tax=A(580).tax_amount,
                             discounts=A(-20).net_amount)

    def test_happy_path_scenario(self):
        """ Tests the simple job life cycle from progress invoice to final payment.
        """
        debit_jobs([(self.job, A(480), Entry.FLAT_DEBIT)])  # progress invoice
        credit_jobs([(self.job, A(100), A(0), A(0))], D(100))  # progress payment
        debit_jobs([(self.job, A(480), Entry.FLAT_DEBIT)], recognize_revenue=True)  # final invoice
        credit_jobs([(self.job, A(800), A(60), A(0))], D(800))  # final payment

        self.assert_balances(bank=A(900, 0, 0),
                             invoiced=A(960), paid=A(-960),
                             debited=A(480*2 + 380), credited=A(-480*2 - 380),
                             income=A(960).net_amount, tax=A(900).tax_amount,
                             discounts=A(-60).net_amount)

        total_income = income_account().balance + discount_account().balance
        self.assertEqual(total_income, A(900).net_amount)

    @skip
    def test_refund_to_other_job_and_customer_with_recognized_revenue(self):
        """ Refund one job and apply part of the refund to second job and return the rest to customer. """

        debit_jobs([(self.job, A(480), Entry.WORK_DEBIT),
                    (self.job2, A(200), Entry.WORK_DEBIT)], recognize_revenue=True)

        credit_jobs([(self.job, A(880), A(0), A(0))], D(880))

        self.assert_balances(bank=A(880, 0, 0), balance=A(480)-A(880),
                             invoiced=A(480), paid=A(-880),
                             income=A(680).net_amount, tax=A(680).tax_amount)

        self.assert_balances(bank=A(880, 0, 0), balance=A(200),
                             invoiced=A(200),
                             income=A(680).net_amount, tax=A(680).tax_amount,
                             switch_to_job=self.job2)

        a400 = A(880)-A(480)
        adjust_jobs([(self.job, A(0), a400, A(0)),
                     (self.job2, A(0), A(0), a400-A(200))])

        self.assert_balances(bank=A(680, 0, 0), balance=A(0),
                             invoiced=A(480), paid=A(-480),
                             debited=A(880), credited=A(-880),
                             income=A(680).net_amount, tax=A(680).tax_amount)

        self.assert_balances(bank=A(680, 0, 0), balance=A(0),
                             invoiced=A(200), paid=A(-200),
                             income=A(680).net_amount, tax=A(680).tax_amount,
                             switch_to_job=self.job2)

    @skip
    def test_refund_to_customer_on_final_invoice_after_complicated_transactions(self):
        # we send a partial invoice for $410
        debit_jobs([(self.job, A(210), Entry.WORK_DEBIT),
                    (self.job2, A(200), Entry.WORK_DEBIT)])

        # customer overpays by $100, we apply overpayment to first job
        credit_jobs([(self.job, A(310), A(0), A(0)),
                     (self.job2, A(200), A(0), A(0))], D(510))

        # issue final invoice and add $100 extra debit to first job, consuming the overpayment
        # job2 gets some new work charged as well
        debit_jobs([(self.job, A(100), Entry.WORK_DEBIT),  # gets swallowed by overpayment
                    (self.job2, A(100), Entry.WORK_DEBIT)],  # adds to amount due
                   recognize_revenue=True)

        a610 = A(510) + A(100)
        self.assert_balances(bank=A(510, 0, 0),
                             invoiced=A(310), paid=A(-310),
                             income=a610.net_amount, tax=a610.tax_amount)
        self.assert_balances(bank=A(510, 0, 0), balance=A(100),
                             invoiced=A(300), paid=A(-200),
                             income=a610.net_amount, tax=a610.tax_amount,
                             switch_to_job=self.job2)

        # customer overpays final invoice by $50
        credit_jobs([(self.job2, A(150), A(0), A(0))], D(150))

        # overpayment only affects the job balance, income/tax are unchanged
        self.assert_balances(bank=A(660, 0, 0),
                             invoiced=A(310), paid=A(-310),
                             income=a610.net_amount, tax=a610.tax_amount)
        self.assert_balances(bank=A(660, 0, 0), balance=A(-50.00),
                             invoiced=A(300), paid=A(-350),
                             income=a610.net_amount, tax=a610.tax_amount,
                             switch_to_job=self.job2)

        # refund customer the overpayment
        adjust_jobs([(self.job2, A(0), A(50), A(0))])

        self.assert_balances(bank=A(610, 0, 0),
                             invoiced=A(310), paid=A(-310),
                             income=a610.net_amount, tax=a610.tax_amount)
        self.assert_balances(bank=A(610, 0, 0),
                             invoiced=A(300), paid=A(-300),
                             debited=A(350), credited=A(-350),
                             income=a610.net_amount, tax=a610.tax_amount,
                             switch_to_job=self.job2)


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

