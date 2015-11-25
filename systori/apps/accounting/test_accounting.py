from decimal import Decimal as D
from django.test import TestCase
from systori.lib.accounting.tools import extract_net_tax, compute_gross_tax
from ..task.test_models import create_task_data
from .models import Account, Transaction, Entry, create_account_for_job
from .skr03 import create_chart_of_accounts
from .skr03 import debit_jobs, credit_jobs
from .constants import *


def create_data(self):
    create_task_data(self)
    create_chart_of_accounts(self)
    self.job.account = create_account_for_job(self.job)
    self.job.save()
    self.job2.account = create_account_for_job(self.job2)
    self.job2.save()


class TestAccountDelete(TestCase):
    def setUp(self):
        create_data(self)

    def test_delete_account_when_job_is_deleted(self):
        account_id = self.job.account.id
        self.assertTrue(Account.objects.filter(id=account_id).exists())
        self.job.delete()
        self.assertFalse(Account.objects.filter(id=account_id).exists())


class ProgressBilling(TestCase):

    def setUp(self):
        create_data(self)

    def test_before_any_progress_debits(self):
        # account balance should be 0
        self.assertEquals(0, self.job.account.balance)
        # no payment liabilities either
        self.assertEquals(0, promised_payments().balance)

    def test_first_progress_debit(self):
        debit_jobs([(self.job, D(480.00), Entry.WORK_DEBIT)])
        self.assertEquals(D(480.00), self.job.account.balance)
        self.assertEquals(D(480.00), promised_payments().balance)

    def test_first_progress_debit_and_full_payment(self):
        debit_jobs([(self.job, D(480.00), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, D(480.00), D(0), D(0))], D(480.00))
        self.assertEquals(0, self.job.account.balance)
        self.assertEquals(0, promised_payments().balance)

    def test_first_progress_debit_and_credit(self):
        debit_jobs([(self.job, D(500.00), Entry.WORK_DEBIT)])
        credit_jobs([(self.job, D(480.00), D(0), D(0))], D(480.00))
        self.assertEquals(D(20.00), self.job.account.balance)
        self.assertEquals(D(20.00), promised_payments().balance)


class TestPartialCredit(TestCase):
    def setUp(self):
        create_data(self)
        debit_jobs([(self.job, D(480.00), Entry.FLAT_DEBIT)])

    def test_partial_credit(self):
        credit_jobs([(self.job, D(400), D(0), D(0))], D(400))
        net, tax = extract_net_tax(D(400), TAX_RATE)
        self.assertEquals(D(80), self.job.account.balance)
        self.assertEquals(D(80), promised_payments().balance)
        self.assertEquals(net, partial_payments().balance)
        self.assertEquals(tax, tax_account().balance)

    def test_partial_credit_w_discount(self):
        credit_jobs([(self.job, D(320), D(80), D(0))], D(320))
        net, tax = extract_net_tax(D(320), TAX_RATE)
        self.assertEquals(D(80), self.job.account.balance)
        self.assertEquals(D(80), promised_payments().balance)
        self.assertEquals(net, partial_payments().balance)
        self.assertEquals(tax, tax_account().balance)

    def test_partial_credit_in_full(self):
        credit_jobs([(self.job, D(480), D(0), D(0))], D(480))
        net, tax = extract_net_tax(D(480), TAX_RATE)
        self.assertEquals(0, self.job.account.balance)
        self.assertEquals(0, promised_payments().balance)
        self.assertEquals(net, partial_payments().balance)
        self.assertEquals(tax, tax_account().balance)

    def test_partial_credit_in_full_w_discount(self):
        credit_jobs([(self.job, D(432), D(48), D(0))], D(432))
        net, tax = extract_net_tax(D(432), TAX_RATE)
        self.assertEquals(0, self.job.account.balance)
        self.assertEquals(0, promised_payments().balance)
        self.assertEquals(net, partial_payments().balance)
        self.assertEquals(tax, tax_account().balance)


class TestMultiAccountPartialCredit(TestCase):
    EXPECTED_BALANCE = round(D(480.00) * D(1.19) - D(400), 2)

    def setUp(self):
        create_data(self)
        debit_jobs([(self.job, D(480.00), Entry.FLAT_DEBIT)])
        debit_jobs([(self.job2, D(480.00), Entry.WORK_DEBIT)])

    def test_multi_partial_credit_w_discount(self):
        self.assertEquals(D(480), self.job.account.balance)
        self.assertEquals(D(480), self.job2.account.balance)
        self.assertEquals(D(960), promised_payments().balance)
        credit_jobs([
            (self.job, D(480), D(0), D(0)),
            (self.job2, D(440), D(40), D(0))
        ], D(920))
        net, tax = extract_net_tax(D(920), TAX_RATE)
        self.assertEquals(D(0), self.job.account.balance)
        self.assertEquals(D(0), self.job2.account.balance)
        self.assertEquals(D(0), promised_payments().balance)
        self.assertEquals(net, partial_payments().balance)
        self.assertEquals(tax, tax_account().balance)


class TestSubsequentDebit(TestCase):
    def setUp(self):
        create_data(self)

        self.task.complete = 5
        self.task.save()
        debit_jobs([(self.job, round(D(480.00) * D(1.19), 2), False)])
        credit_jobs([(self.job, D(480) * D(1.19), D(0))],
                       D(480) * D(1.19))  # a full payment

        self.task.complete += 2
        self.task.save()

    def test_subsequent_partial_debit(self):
        self.assertEquals(D(0), self.job.account.balance)
        debit_jobs([(self.job, round(D(192.00) * D(1.19), 2), False)])
        self.assertEquals(round(D(192.0) * D(1.19), 2), self.job.account.balance)


class TestFinalDebit(TestCase):
    def setUp(self):
        create_data(self)

    def test_revenue_recognized_debit_with_no_previous_debits_or_credits(self):
        debit_jobs([(self.job, D(960.00), Entry.FLAT_DEBIT)], recognize_revenue=True)
        self.assertEquals(D(960.00), self.job.account.balance)
        net, tax = extract_net_tax(D(960.00), TAX_RATE)
        self.assertEquals(net, income_account().balance)
        self.assertEquals(tax, tax_account().balance)
        self.assertEquals(0, promised_payments().balance)  # revenue is recognized, so no promised payments
        self.assertEquals(0, partial_payments().balance)

    def test_final_invoice_with_previous_debit(self):
        debit_jobs([(self.job, D(480.00), Entry.FLAT_DEBIT)])
        self.assertEquals(D(480.00), promised_payments().balance)

        debit_jobs([(self.job, D(480.00), Entry.FLAT_DEBIT)], recognize_revenue=True)
        self.assertEquals(0, promised_payments().balance)
        self.assertEquals(D(960.00), self.job.account.balance)

        net, tax = extract_net_tax(D(960.00), TAX_RATE)
        self.assertEquals(net, income_account().balance)
        self.assertEquals(tax, tax_account().balance)
        self.assertEquals(0, partial_payments().balance)

    def test_final_invoice_with_previous_debit_and_credit(self):
        debit_jobs([(self.job, D(480.00), Entry.FLAT_DEBIT)])
        self.assertEquals(D(480.00), promised_payments().balance)

        net, tax = extract_net_tax(D(480.00), TAX_RATE)
        credit_jobs([(self.job, D(480.00), D(0), D(0))], D(480.0))
        self.assertEquals(0, promised_payments().balance)
        self.assertEquals(net, partial_payments().balance)
        self.assertEquals(tax, tax_account().balance)

        debit_jobs([(self.job, D(480.00), Entry.FLAT_DEBIT)], recognize_revenue=True)
        self.assertEquals(0, promised_payments().balance)
        self.assertEquals(D(480.00), self.job.account.balance)

        net, tax = extract_net_tax(D(960.00), TAX_RATE)
        self.assertEquals(net, income_account().balance)
        self.assertEquals(tax, tax_account().balance)
        self.assertEquals(0, partial_payments().balance)

    def test_final_invoice_with_previous_debit_and_discount_credit(self):
        debit_jobs([(self.job, D(500.00), Entry.FLAT_DEBIT)])

        net, tax = extract_net_tax(D(450.00), TAX_RATE)
        credit_jobs([(self.job, D(450.00), D(50.00), D(0))], D(450.0))
        self.assertEquals(0, self.job.account.balance)
        self.assertEquals(0, promised_payments().balance)
        self.assertEquals(net, partial_payments().balance)
        self.assertEquals(tax, tax_account().balance)

        debit_jobs([(self.job, D(480.00), Entry.FLAT_DEBIT)], recognize_revenue=True)

        net, tax = extract_net_tax(D(930.00), TAX_RATE)
        self.assertEquals(D(480.00), self.job.account.balance)
        self.assertEquals(net, income_account().balance)
        self.assertEquals(tax, tax_account().balance)
        self.assertEquals(0, partial_payments().balance)


class TestPaymentAfterFinalDebit(TestCase):
    def setUp(self):
        create_data(self)

    def test_payment_after_final_invoice_with_previous_debit(self):
        debit_jobs([(self.job, D(480.00), Entry.FLAT_DEBIT)])
        credit_jobs([(self.job, D(100.00), D(0), D(0))], D(100.00))
        debit_jobs([(self.job, D(480.00), Entry.FLAT_DEBIT)], recognize_revenue=True)
        credit_jobs([(self.job, D(800.00), D(60), D(0))], D(800.00))

        income, tax = extract_net_tax(D(900), TAX_RATE)
        self.assertEquals(D(0), self.job.account.balance)
        self.assertEquals(D(0), promised_payments().balance)
        self.assertEquals(D(0), partial_payments().balance)
        self.assertEquals(D(900.00), bank_account().balance)
        self.assertEquals(income, income_account().balance)
        self.assertEquals(tax, tax_account().balance)
        self.assertEquals(D(60), discount_account().balance)


class TestDeleteTransaction(TestCase):
    def setUp(self):
        create_data(self)
        credit_jobs([(self.job, D(100), D(0), D(0))], D(100))

    def test_that_all_entries_are_also_deleted(self):
        self.assertEquals(D(-100.00), self.job.account.balance)
        Transaction.objects.first().delete()
        self.assertEquals(D(0), self.job.account.balance)


def promised_payments(): return Account.objects.get(code=SKR03_PROMISED_PAYMENTS_CODE)
def partial_payments(): return Account.objects.get(code=SKR03_PARTIAL_PAYMENTS_CODE)
def income_account(): return Account.objects.get(code=SKR03_INCOME_CODE)
def tax_account(): return Account.objects.get(code=SKR03_TAX_PAYMENTS_CODE)
def discount_account(): return Account.objects.get(code=SKR03_CASH_DISCOUNT_CODE)
def bank_account(): return Account.objects.get(code=SKR03_BANK_CODE)
