from decimal import Decimal as D
from django.test import TestCase
from systori.lib.accounting.tools import extract_net_tax, compute_gross_tax
from ..task.test_models import create_task_data
from .models import Account, Transaction, Entry, create_account_for_job
from .workflow import create_chart_of_accounts
from .workflow import debit_jobs, credit_jobs
from .constants import *


def create_data(self):
    create_task_data(self)
    create_chart_of_accounts(self)
    self.job.account = create_account_for_job(self.job)
    self.job.save()
    self.job2.account = create_account_for_job(self.job2)
    self.job2.save()


class TestDeletingThings(TestCase):
    def setUp(self):
        create_data(self)
        credit_jobs([(self.job, D(100), D(0), D(0))], D(100))

    def test_that_all_entries_are_also_deleted(self):
        self.assertEquals(D(-100.00), self.job.account.balance)
        Transaction.objects.first().delete()
        self.assertEquals(D(0), self.job.account.balance)

    def test_delete_account_when_job_is_deleted(self):
        account_id = self.job.account.id
        self.assertTrue(Account.objects.filter(id=account_id).exists())
        self.job.delete()
        self.assertFalse(Account.objects.filter(id=account_id).exists())


class TestCompletedContractAccountingMethod(TestCase):
    """ http://accountingexplained.com/financial/revenue/completed-contract-method """

    def setUp(self):
        create_data(self)

    def assert_balances(self, job=0, job_debits=None, job_adjusted_debits=None,
                        promised=0, partial=0, tax=0, income=0, discounts=0, bank=0,
                        switch_to_job=None):

        if switch_to_job is not None:
            original_job = self.job
            self.job = switch_to_job

        self.assertEquals(job, self.job.account.balance)

        if job_debits is None:
            job_debits = self.job.account.debits().total
        else:
            self.assertEquals(job_debits, self.job.account.debits().total)

        if job_adjusted_debits is None:
            job_adjusted_debits = job_debits
        self.assertEquals(job_adjusted_debits, self.job.account.adjusted_debits_total)

        self.assertEquals(promised, promised_payments().balance)
        self.assertEquals(partial, partial_payments().balance)
        self.assertEquals(tax, tax_account().balance)
        self.assertEquals(income, income_account().balance)
        self.assertEquals(discounts, discount_account().balance)
        self.assertEquals(bank, bank_account().balance)

        if switch_to_job:
            self.job = original_job

    # Before Revenue Recognition

    def test_before_any_progress_debits(self):
        # everything starts off at 0
        self.assert_balances()

    def test_progress_debit(self):
        debit_jobs([(self.job, D(480.00), Entry.WORK_DEBIT)])
        self.assert_balances(promised=D(480.00), job=D(480.00))  # <- gross we're owed

    def test_payment(self):
        """ Best case is when payment matches debit. """
        debit_jobs([(self.job, D(480.00), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, D(480.00), D(0), D(0))], D(480.00))
        net, tax = extract_net_tax(D(480.00), TAX_RATE)
        self.assert_balances(bank=D(480.00), partial=net, tax=tax)  # <- cash

    def test_overpayment(self):
        """ Customer pays more than was debited causing negative account balance. """
        debit_jobs([(self.job, D(500.00), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, D(580.00), D(0), D(0))], D(580.00))
        net, tax = extract_net_tax(D(580.00), TAX_RATE)
        self.assert_balances(bank=D(580.00), partial=net, tax=tax,  # <- cash
                             job=D(-80), promised=D(-80),  # <- negative balances because of overpayment
                             job_debits=D(500.00), job_adjusted_debits=D(500.00))

    def test_underpayment(self):
        """ Customer pays less than was debited without any discounts or adjustments applied. """
        debit_jobs([(self.job, D(500.00), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, D(480.00), D(0), D(0))], D(480.00))
        net, tax = extract_net_tax(D(480.00), TAX_RATE)
        self.assert_balances(bank=D(480.00), partial=net, tax=tax,  # <- cash
                             job=D(20), promised=D(20),  # <- gross we're still owed
                             job_debits=D(500.00), job_adjusted_debits=D(500.00))  # no adjustment

    def test_adjusted_payment_matching_debit(self):
        """ Payment entered along with an adjustment to exactly match the debit. """
        debit_jobs([(self.job, D(500.00), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, D(480.00), D(0), D(20.00))], D(480.00))
        net, tax = extract_net_tax(D(480.00), TAX_RATE)
        self.assert_balances(bank=D(480.00), partial=net, tax=tax,  # <- cash
                             job=D(0), promised=D(0),  # <- zero balance because we added adjustment
                             job_debits=D(500.00), job_adjusted_debits=D(480.00))  # <- 20.00 adjusted

    def test_adjusted_payment_below_debit(self):
        """ Payment entered along with an adjustment but still not enough to cover the debit. """
        debit_jobs([(self.job, D(600.00), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, D(480.00), D(0), D(20.00))], D(480.00))
        net, tax = extract_net_tax(D(480.00), TAX_RATE)
        self.assert_balances(bank=D(480.00), partial=net, tax=tax,  # <- cash
                             job=D(100.00), promised=D(100.00),  # <- owed balance because adjustment wasn't enough
                             job_debits=D(600.00), job_adjusted_debits=D(580.00))  # <- 20.00 adjusted

    def test_discounted_payment_matching_debit(self):
        """ Payment entered along with a discount to exactly match the debit. """
        debit_jobs([(self.job, D(500.00), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, D(480.00), D(20.00), D(0))], D(480.00))
        net, tax = extract_net_tax(D(480.00), TAX_RATE)
        self.assert_balances(bank=D(480.00), partial=net, tax=tax,  # <- cash
                             job=D(0), promised=D(0),  # <- zero balance
                             job_debits=D(500.00), job_adjusted_debits=D(500.00))  # <- discounts don't adjust anything

    def test_discounted_payment_below_debit(self):
        """ Payment entered along with a discount but still not enough to cover the debit. """
        debit_jobs([(self.job, D(600.00), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, D(480.00), D(20.00), D(0))], D(480.00))
        net, tax = extract_net_tax(D(480.00), TAX_RATE)
        self.assert_balances(bank=D(480.00), partial=net, tax=tax,  # <- cash
                             job=D(100.00), promised=D(100.00),  # <- owed balance because discount wasn't enough
                             job_debits=D(600.00), job_adjusted_debits=D(600.00))  # <- discounts don't adjust anything

    def test_split_payment_with_discount_and_adjustment(self):
        """ Split payment where one job is discounted and another is adjusted. """
        debit_jobs([
            (self.job, D(480.00), Entry.FLAT_DEBIT),
            (self.job2, D(480.00), Entry.WORK_DEBIT)
        ])
        self.assertEquals(D(480), self.job2.account.balance)
        self.assert_balances(promised=D(960.00), job=D(480.00))
        credit_jobs([
            (self.job, D(440), D(0), D(40.00)),  # adjusted
            (self.job2, D(460), D(20.00), D(0)),  # discounted
        ], D(900))
        net, tax = extract_net_tax(D(900), TAX_RATE)
        self.assert_balances(bank=D(900.00), partial=net, tax=tax,  # <- cash
                             job=D(0), promised=D(0),  # <- zero balance because we added adjustments and discounts
                             job_debits=D(480.00), job_adjusted_debits=D(440.00))  # <- 40.00 adjusted
        self.assert_balances(bank=D(900.00), partial=net, tax=tax,  # <- cash
                             job=D(0), promised=D(0),  # <- zero balance because we added adjustments and discounts
                             job_debits=D(480.00), job_adjusted_debits=D(480.00),  # used discount instead of adjustments
                             switch_to_job=self.job2)

    # After Revenue Recognition

    def test_revenue_debits(self):
        """ Enter a debit and enable revenue recognition, then perform another debit but this time
            without explicit revenue recognition since job already knows it's in revenue recognition mode.
        """
        debit_jobs([(self.job, D(480.00), Entry.WORK_DEBIT)], recognize_revenue=True)
        net, tax = extract_net_tax(D(480.00), TAX_RATE)
        self.assert_balances(job=D(480.00), income=net, tax=tax)  # <- gross we're owed

        debit_jobs([(self.job, D(480.00), Entry.WORK_DEBIT)])  # this job is already in revenue recognition mode
        net, tax = extract_net_tax(D(960.00), TAX_RATE)
        self.assert_balances(job=D(960.00), income=net, tax=tax)  # <- gross we're owed

    def test_previous_revenue_gets_recognized(self):
        """ Create a debit and an underpayment then transition this job into revenue recognition mode
            without actually entering any new work debits. This should move all previously promised and
            cash revenues into the main income account.
        """
        debit_jobs([(self.job, D(480.00), Entry.FLAT_DEBIT)])  # some promised revenue
        credit_jobs([(self.job, D(200.00), D(0), D(0))], D(200.00))  # some cash revenue
        net, tax = extract_net_tax(D(200.00), TAX_RATE)
        self.assert_balances(bank=D(200.00), partial=net, tax=tax, job=D(280), promised=D(280))

        # trick debit_jobs() into running a zero debit in order to transition job to recognized revenue mode
        debit_jobs([(self.job, D(0.00), Entry.FLAT_DEBIT)], recognize_revenue=True)

        # income now includes the previous promised revenue and cash revenue
        net, tax = extract_net_tax(D(480.00), TAX_RATE)
        self.assert_balances(bank=D(200.00), income=net, tax=tax, job=D(280))

    def test_adjusted_payment_matching_debit_with_recognized_revenue(self):
        """ Payment entered to revenue recognized account along with an adjustment
            to exactly match the debit.
        """
        debit_jobs([(self.job, D(500.00), Entry.WORK_DEBIT)], recognize_revenue=True)
        credit_jobs([(self.job, D(480.00), D(0), D(20.00))], D(480.00))
        net, tax = extract_net_tax(D(480.00), TAX_RATE)
        self.assert_balances(bank=D(480.00), income=net, tax=tax,
                             job_debits=D(500.00), job_adjusted_debits=D(480.00))  # <- 20.00 adjusted

    def test_adjusted_payment_below_debit_with_recognized_revenue(self):
        """ Payment entered to revenue recognized account along with an adjustment
            but still not enough to cover the debit.
        """
        debit_jobs([(self.job, D(600.00), Entry.WORK_DEBIT)], recognize_revenue=True)
        credit_jobs([(self.job, D(480.00), D(0), D(20.00))], D(480.00))
        net, tax = extract_net_tax(D(580.00), TAX_RATE)  # revenue = promised + cash - adjustments
        self.assert_balances(bank=D(480.00), income=net, tax=tax,  # <- income is higher than bank balance
                             job=D(100.00),  # <- job still has some balance
                             job_debits=D(600.00), job_adjusted_debits=D(580.00))  # <- 20.00 adjusted

    def test_discounted_payment_matching_debit_with_recognized_revenue(self):
        """ Payment entered to revenue recognized account along with a cash discount
            to exactly match the debit.
        """
        debit_jobs([(self.job, D(500.00), Entry.WORK_DEBIT)], recognize_revenue=True)
        credit_jobs([(self.job, D(480.00), D(20.00), D(0))], D(480.00))
        net, _ = extract_net_tax(D(500.00), TAX_RATE)  # revenue is not affected by discounts so it stays 500.00
        _, tax = extract_net_tax(D(480.00), TAX_RATE)  # tax on the other hand is reduced by discounts
        net_discount, _ = extract_net_tax(D(20.00), TAX_RATE)  # discounts are gross amounts, so we need the net
        self.assert_balances(bank=D(480.00), income=net, tax=tax,
                             discounts=-net_discount)  # discounts reduce the special 'Cash discounts' account

    def test_discounted_payment_below_debit_with_recognized_revenue(self):
        """ Payment entered to revenue recognized account along with a cash discount
            but still not enough to cover the debit.
        """
        debit_jobs([(self.job, D(600.00), Entry.WORK_DEBIT)], recognize_revenue=True)
        credit_jobs([(self.job, D(480.00), D(20.00), D(0))], D(480.00))
        net, _ = extract_net_tax(D(600.00), TAX_RATE)  # revenue is not affected by discounts so it stays 600.00
        _, tax = extract_net_tax(D(580.00), TAX_RATE)  # tax on the other hand is reduced by discounts
        net_discount, _ = extract_net_tax(D(20.00), TAX_RATE)  # discounts are gross amounts, so we need the net
        self.assert_balances(bank=D(480.00), income=net, tax=tax, job=D(100.00),
                             discounts=-net_discount)  # discounts reduce the special 'Cash discounts' account

    def test_happy_path_scenario(self):
        """ Tests the simple job life cycle from progress invoice to final payment.
        """
        debit_jobs([(self.job, D(480.00), Entry.FLAT_DEBIT)])  # progress invoice
        credit_jobs([(self.job, D(100.00), D(0), D(0))], D(100.00))  # progress payment
        debit_jobs([(self.job, D(480.00), Entry.FLAT_DEBIT)], recognize_revenue=True)  # final invoice
        credit_jobs([(self.job, D(800.00), D(60), D(0))], D(800.00))  # final payment

        net, _ = extract_net_tax(D(960.00), TAX_RATE)  # revenue is not affected by discounts so it stays 960.00
        _, tax = extract_net_tax(D(900.00), TAX_RATE)  # tax on the other hand is reduced by discounts
        net_discount, _ = extract_net_tax(D(60.00), TAX_RATE)  # discounts are gross amounts, so we need the net
        self.assert_balances(bank=D(900.00), income=net, tax=tax, discounts=-net_discount)

        total_income = income_account().balance + discount_account().balance
        self.assertEqual(total_income, net-net_discount)


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
