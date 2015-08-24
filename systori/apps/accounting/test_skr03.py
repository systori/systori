from decimal import Decimal
from django.test import TestCase
from django.db import IntegrityError
from django.utils.translation import activate
from ..task.test_models import create_task_data
from ..company.models import Company
from ..task.models import Job
from .models import *
from .skr03 import *
from .forms import *


def create_data(self):
    create_task_data(self)
    create_chart_of_accounts(self)
    self.job.account = create_account_for_job(self.job)
    self.job.save()
    self.job2.account = create_account_for_job(self.job2)
    self.job2.save()


class TestExceptions(TestCase):
    def setUp(self):
        create_data(self)

    def test_payments_discounts_on_non_customer_account(self):
        self.assertRaisesMessage(Job.DoesNotExist, "Account has no job.", self.income.payments)
        self.assertRaisesMessage(Job.DoesNotExist, "Account has no job.", self.income.discounts)

    def test_creating_account_for_project(self):
        self.assertRaisesMessage(IntegrityError,
                                 "Account with code %s already exists." % '1{:04}'.format(self.job.id),
                                 create_account_for_job, self.job)

        self.job.id = DEBTOR_CODE_RANGE[1] - DEBTOR_CODE_RANGE[0] + 1
        self.assertRaisesMessage(ValueError,
                                 "Account id %s is outside the maximum range of %s." % (
                                 DEBTOR_CODE_RANGE[1] + 1, DEBTOR_CODE_RANGE[1]),
                                 create_account_for_job, self.job)


class TestAccountDelete(TestCase):
    def setUp(self):
        create_data(self)

    def test_delete_account_when_project_is_deleted(self):
        account_id = self.job.account.id
        self.assertTrue(Account.objects.filter(id=account_id).exists())
        self.job.delete()
        self.assertFalse(Account.objects.filter(id=account_id).exists())


class TestBankAccountForm(TestCase):
    def setUp(self):
        create_data(self)

    def test_form_initial_incremented_code(self):
        self.assertEquals(str(BANK_CODE_RANGE[0] + 1), BankAccountForm().initial['code'])

    def test_form_edit_code(self):
        self.assertEquals("hi", BankAccountForm(instance=Account.objects.create(code="hi")).initial['code'])

    def test_valid_code(self):
        self.assertTrue(BankAccountForm({'code': '1200'}).is_valid())
        self.assertTrue(BankAccountForm({'code': '1288'}).is_valid())

    def test_invalid_code(self):
        activate('en')
        self.assertFalse(BankAccountForm({'code': 'foo'}).is_valid())
        self.assertFalse(BankAccountForm({'code': '1199'}).is_valid())
        self.assertFalse(BankAccountForm({'code': '1289'}).is_valid())

        form = BankAccountForm({'code': '1a'})
        self.assertEquals('Account code must be a number between 1200 and 1288 inclusive.', form.errors['code'][0])


class TestInitialPartialDebit(TestCase):
    def setUp(self):
        create_data(self)
        self.task.complete = 5
        self.task.save()

    def test_before_any_debits(self):
        # account balance should be 0
        self.assertEquals(0, self.job.account.balance)
        # there is a job that can be billed
        self.assertEquals(Decimal(480), self.job.billable_total)
        self.assertEquals(1, len(list(self.project.billable_jobs)))
        # no payment liabilities either
        self.assertEquals(0, Account.objects.get(code="1710").balance)

    def test_initial_partial_debit(self):
        partial_debit(self.job)
        self.assertEquals(round(Decimal(480.00) * Decimal(1.19), 2), self.job.account.balance)
        self.assertEquals(round(Decimal(480.00) * Decimal(1.19), 2), Account.objects.get(code="1710").balance)

    def test_initial_partial_debit_with_prepayment(self):
        self.task.complete += 2
        self.task.save()
        partial_credit([(self.job, Decimal(480.00) * Decimal(1.19), Decimal(0))], Decimal(480.00) * Decimal(1.19))
        partial_debit(self.job)
        self.assertEquals(round(Decimal(192.0) * Decimal(1.19), 2), self.job.account.balance)


class TestPartialCredit(TestCase):
    EXPECTED_BALANCE = round(Decimal(480.00) * Decimal(1.19) - Decimal(400), 2)

    def setUp(self):
        create_data(self)
        self.task.complete = 5
        self.task.save()
        partial_debit(self.job)

    def test_partial_credit(self):
        partial_credit([(self.job, Decimal(400), Decimal(0))], Decimal(400))
        self.assertEquals(self.EXPECTED_BALANCE, self.job.account.balance)
        self.assertEquals(self.EXPECTED_BALANCE, Account.objects.get(code="1710").balance)
        self.assertEquals(round(Decimal(400) / Decimal(1.19), 2), Account.objects.get(code="1718").balance)
        self.assertEquals(round(Decimal(400) / Decimal(1.19) * Decimal(.19), 2),
                          Account.objects.get(code="1776").balance)

    def test_partial_credit_w_discount(self):
        # different payment amount but ending balances are the same because discount was applied
        partial_credit([(self.job, Decimal(360), Decimal(0.1))], Decimal(360))
        self.assertEquals(self.EXPECTED_BALANCE, self.job.account.balance)
        self.assertEquals(self.EXPECTED_BALANCE, Account.objects.get(code="1710").balance)
        self.assertEquals(round(Decimal(360) / Decimal(1.19), 2), Account.objects.get(code="1718").balance)
        self.assertEquals(round(Decimal(360) / Decimal(1.19) * Decimal(.19), 2),
                          Account.objects.get(code="1776").balance)

    def test_partial_credit_in_full(self):
        partial_credit([(self.job, Decimal(480) * Decimal(1.19), Decimal(0))], Decimal(480) * Decimal(1.19))
        self.assertEquals(Decimal(0), self.job.account.balance)
        self.assertEquals(Decimal(0), Account.objects.get(code="1710").balance)
        self.assertEquals(round(Decimal(480), 2), Account.objects.get(code="1718").balance)
        self.assertEquals(round(Decimal(480) * Decimal(.19), 2), Account.objects.get(code="1776").balance)

    def test_partial_credit_in_full_w_discount(self):
        # different payment amount but ending balance is still 0 because discount was applied
        partial_credit([(self.job, Decimal(432) * Decimal(1.19), Decimal(0.1))], Decimal(432) * Decimal(1.19))
        self.assertEquals(Decimal(0), self.job.account.balance)
        self.assertEquals(Decimal(0), Account.objects.get(code="1710").balance)
        self.assertEquals(round(Decimal(432), 2), Account.objects.get(code="1718").balance)
        self.assertEquals(round(Decimal(432) * Decimal(.19), 2), Account.objects.get(code="1776").balance)


class TestMultiAccountPartialCredit(TestCase):
    EXPECTED_BALANCE = round(Decimal(480.00) * Decimal(1.19) - Decimal(400), 2)

    def setUp(self):
        create_data(self)
        self.task.complete = 5
        self.task.save()

        self.task3.complete = 5
        self.task3.save()

        partial_debit(self.job)
        partial_debit(self.job2)

    def test_multi_partial_credit_w_discount(self):
        self.assertEquals(round(Decimal(480) * Decimal(1.19), 2), self.job.account.balance)
        self.assertEquals(round(Decimal(480) * Decimal(1.19), 2), self.job2.account.balance)
        self.assertEquals(round(Decimal(960) * Decimal(1.19), 2), Account.objects.get(code="1710").balance)
        partial_credit([
            (self.job, round(Decimal(480) * Decimal(1.19), 2), Decimal(0)),
            (self.job2, round(Decimal(432) * Decimal(1.19), 2), Decimal(0.1))
        ], round(Decimal(480) * Decimal(1.19) + Decimal(432) * Decimal(1.19), 2))
        self.assertEquals(Decimal(0), self.job.account.balance)
        self.assertEquals(Decimal(0), self.job2.account.balance)
        self.assertEquals(Decimal(0), Account.objects.get(code="1710").balance)
        self.assertEquals(round(Decimal(912), 2), Account.objects.get(code="1718").balance)
        self.assertEquals(round(Decimal(912) * Decimal(.19), 2), Account.objects.get(code="1776").balance)


class TestSubsequentDebit(TestCase):
    def setUp(self):
        create_data(self)

        self.task.complete = 5
        self.task.save()
        partial_debit(self.job)  # first invoice
        partial_credit([(self.job, Decimal(480) * Decimal(1.19), Decimal(0))],
                       Decimal(480) * Decimal(1.19))  # a full payment

        self.task.complete += 2
        self.task.save()

    def test_subsequent_partial_debit(self):
        self.assertEquals(Decimal(0), self.job.account.balance)
        partial_debit(self.job)
        self.assertEquals(round(Decimal(192.0) * Decimal(1.19), 2), self.job.account.balance)


class TestFinalDebit(TestCase):
    def setUp(self):
        create_data(self)

    def test_final_debit_no_previous_debits_or_credits(self):
        self.task.complete = 10
        self.task.save()
        final_debit(self.job)

        self.assertEquals(round(Decimal(960.00) * Decimal(1.19), 2), self.job.account.balance)
        self.assertEquals(round(Decimal(960.00), 2), Account.objects.get(code="8400").balance)
        self.assertEquals(round(Decimal(960.00) * Decimal(0.19), 2), Account.objects.get(code="1776").balance)
        self.assertEquals(0, Account.objects.get(code="1718").balance)

    def test_final_invoice_with_previous_debit(self):
        self.task.complete = 5
        self.task.save()
        partial_debit(self.job)

        self.task.complete += 5
        self.task.save()
        final_debit(self.job)

        self.assertEquals(round(Decimal(960.00) * Decimal(1.19), 2), self.job.account.balance)
        self.assertEquals(round(Decimal(960.00), 2), Account.objects.get(code="8400").balance)
        self.assertEquals(round(Decimal(960.00) * Decimal(0.19), 2), Account.objects.get(code="1776").balance)
        self.assertEquals(0, Account.objects.get(code="1718").balance)

    def test_final_invoice_with_previous_debit_and_credit(self):
        self.task.complete = 5
        self.task.save()

        partial_debit(self.job)
        partial_credit([(self.job, Decimal(400) * Decimal(1.19), Decimal(0))], Decimal(400) * Decimal(1.19))

        self.task.complete += 5
        self.task.save()
        final_debit(self.job)

        self.assertEquals(round(Decimal(560.00) * Decimal(1.19), 2), self.job.account.balance)
        self.assertEquals(round(Decimal(960.00), 2), Account.objects.get(code="8400").balance)
        self.assertEquals(round(Decimal(960.00) * Decimal(0.19), 2), Account.objects.get(code="1776").balance)
        self.assertEquals(0, Account.objects.get(code="1718").balance)

    def test_final_invoice_with_previous_debit_and_discount_credit(self):
        self.task.complete = 5
        self.task.save()

        partial_debit(self.job)
        payment = Decimal(400) * Decimal(0.9)
        partial_credit([(self.job, payment * Decimal(1.19), Decimal(0.1))], payment * Decimal(1.19))

        self.task.complete += 5
        self.task.save()
        final_debit(self.job)

        self.assertEquals(round(Decimal(560.00) * Decimal(1.19), 2), self.job.account.balance)
        self.assertEquals(round(Decimal(920.00), 2), Account.objects.get(code="8400").balance)
        self.assertEquals(round(payment * Decimal(0.19) + Decimal(560.00) * Decimal(0.19), 2),
                          Account.objects.get(code="1776").balance)
        self.assertEquals(0, Account.objects.get(code="1718").balance)


class TestPaymentAfterFinalDebit(TestCase):
    def setUp(self):
        create_data(self)

    def test_payment_after_final_invoice_with_previous_debit(self):
        self.task.complete = 5
        self.task.save()
        partial_debit(self.job)
        first_payment = round(Decimal(100.00) * Decimal(1.19), 2)
        partial_credit([(self.job, first_payment, Decimal(0))], first_payment)

        self.task.complete += 5
        self.task.save()
        final_debit(self.job)

        self.project.begin_settlement()

        second_payment = round(Decimal(860.00) * Decimal(1.19) * Decimal(.9), 2)

        partial_credit([(self.job, second_payment, Decimal(.1))], second_payment)

        income = round((first_payment+second_payment) / Decimal(1+.19), 2)
        taxes = round((first_payment+second_payment) - income, 2)

        self.assertEquals(Decimal(0), self.job.account.balance)
        self.assertEquals(Decimal(0), Account.objects.get(code="1710").balance)
        self.assertEquals(Decimal(0), Account.objects.get(code="1718").balance)
        self.assertEquals(taxes, Account.objects.get(code="1776").balance)
        self.assertEquals(first_payment+second_payment, Account.objects.get(code="1200").balance)
        self.assertEquals(round(Decimal(960.00), 2), Account.objects.get(code="8400").balance)
        self.assertEquals(round(Decimal(860)*Decimal(1.19)/Decimal(1+.19) * Decimal(-.1), 2), Account.objects.get(code="8736").balance)


class TestDeleteTransaction(TestCase):
    def setUp(self):
        create_data(self)
        partial_credit([(self.job, Decimal(100), Decimal(0))], Decimal(100))

    def test_that_all_entries_are_also_deleted(self):
        self.assertEquals(Decimal(-100.00), self.job.account.balance)
        Transaction.objects.first().delete()
        self.assertEquals(Decimal(0), self.job.account.balance)
