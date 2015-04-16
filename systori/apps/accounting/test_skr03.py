from decimal import Decimal
from django.test import TestCase
from ..task.test_models import create_task_data
from ..project.models import Project
from .models import *
from .skr03 import *


def create_data(self):
    create_task_data(self)
    create_chart_of_accounts(self)
    self.project.account = Account.objects.create(account_type=Account.ASSET, code="10001")
    self.project.save()


class TestExceptions(TestCase):

    def setUp(self):
        create_data(self)

    def test_payments_discounts_on_non_customer_account(self):
        self.assertRaisesMessage(Project.DoesNotExist, "Account has no project.", self.income.payments)
        self.assertRaisesMessage(Project.DoesNotExist, "Account has no project.", self.income.discounts)


class TestInitialPartialDebit(TestCase):

    def setUp(self):
        create_data(self)
        self.task.complete = 5
        self.task.save()

    def test_before_any_debits(self):
        # account balance should be 0
        self.assertEquals(0, self.project.account.balance)
        # there is a job that can be billed
        self.assertEquals(Decimal(480), self.project.billable_total)
        self.assertEquals(1, len(list(self.project.billable_jobs)))
        # no payment liabilities either
        self.assertEquals(0, Account.objects.get(code="1710").balance)

    def test_initial_partial_debit(self):
        partial_debit(self.project)
        self.assertEquals(round(Decimal(480.00)*Decimal(1.19),2), self.project.account.balance)
        self.assertEquals(round(Decimal(480.00)*Decimal(1.19),2), Account.objects.get(code="1710").balance)

    def test_initial_partial_debit_with_prepayment(self):
        self.task.complete += 2
        self.task.save()
        partial_credit(self.project, Decimal(480.00)*Decimal(1.19))
        partial_debit(self.project)
        self.assertEquals(round(Decimal(192.0)*Decimal(1.19),2), self.project.account.balance)


class TestPartialCredit(TestCase):

    EXPECTED_BALANCE = round(Decimal(480.00)*Decimal(1.19)-Decimal(400),2)

    def setUp(self):
        create_data(self)
        self.task.complete = 5
        self.task.save()
        partial_debit(self.project)

    def test_partial_credit(self):
        partial_credit(self.project, Decimal(400))
        self.assertEquals(self.EXPECTED_BALANCE, self.project.account.balance)
        self.assertEquals(self.EXPECTED_BALANCE, Account.objects.get(code="1710").balance)
        self.assertEquals(round(Decimal(400)/Decimal(1.19),2), Account.objects.get(code="1718").balance)
        self.assertEquals(round(Decimal(400)/Decimal(1.19)*Decimal(.19),2), Account.objects.get(code="1776").balance)

    def test_partial_credit_w_discount(self):
        # different payment amount but ending balances are the same because discount was applied
        partial_credit(self.project, Decimal(360), True)
        self.assertEquals(self.EXPECTED_BALANCE, self.project.account.balance)
        self.assertEquals(self.EXPECTED_BALANCE, Account.objects.get(code="1710").balance)
        self.assertEquals(round(Decimal(360)/Decimal(1.19),2), Account.objects.get(code="1718").balance)
        self.assertEquals(round(Decimal(360)/Decimal(1.19)*Decimal(.19),2), Account.objects.get(code="1776").balance)

    def test_partial_credit_in_full(self):
        partial_credit(self.project, Decimal(480)*Decimal(1.19))
        self.assertEquals(Decimal(0), self.project.account.balance)
        self.assertEquals(Decimal(0), Account.objects.get(code="1710").balance)
        self.assertEquals(round(Decimal(480),2), Account.objects.get(code="1718").balance)
        self.assertEquals(round(Decimal(480)*Decimal(.19),2), Account.objects.get(code="1776").balance)

    def test_partial_credit_in_full_w_discount(self):
        # different payment amount but ending balance is still 0 because discount was applied
        partial_credit(self.project, Decimal(432)*Decimal(1.19), True)
        self.assertEquals(Decimal(0), self.project.account.balance)
        self.assertEquals(Decimal(0), Account.objects.get(code="1710").balance)
        self.assertEquals(round(Decimal(432),2), Account.objects.get(code="1718").balance)
        self.assertEquals(round(Decimal(432)*Decimal(.19),2), Account.objects.get(code="1776").balance)


class TestSubsequentDebit(TestCase):

    def setUp(self):
        create_data(self)

        self.task.complete = 5
        self.task.save()
        partial_debit(self.project) # first invoice
        partial_credit(self.project, Decimal(480)*Decimal(1.19)) # a full payment

        self.task.complete += 2
        self.task.save()

    def test_subsequent_partial_debit(self):
        self.assertEquals(Decimal(0), self.project.account.balance)
        partial_debit(self.project)
        self.assertEquals(round(Decimal(192.0)*Decimal(1.19),2), self.project.account.balance)


class TestFinalDebit(TestCase):

    def setUp(self):
        create_data(self)

    def test_final_debit_no_previous_debits_or_credits(self):
        self.task.complete = 10
        self.task.save()
        final_debit(self.project)

        self.assertEquals(round(Decimal(960.00)*Decimal(1.19),2), self.project.account.balance)
        self.assertEquals(round(Decimal(960.00),2), Account.objects.get(code="8400").balance)
        self.assertEquals(round(Decimal(960.00)*Decimal(0.19),2), Account.objects.get(code="1776").balance)
        self.assertEquals(0, Account.objects.get(code="1718").balance)
        self.assertEquals(0, Account.objects.get(code="8736").balance)

    def test_final_invoice_with_previous_debit(self):
        self.task.complete = 5
        self.task.save()
        partial_debit(self.project)

        self.task.complete += 5
        self.task.save()
        final_debit(self.project)

        self.assertEquals(round(Decimal(960.00)*Decimal(1.19),2), self.project.account.balance)
        self.assertEquals(round(Decimal(960.00),2), Account.objects.get(code="8400").balance)
        self.assertEquals(round(Decimal(960.00)*Decimal(0.19),2), Account.objects.get(code="1776").balance)
        self.assertEquals(0, Account.objects.get(code="1718").balance)
        self.assertEquals(0, Account.objects.get(code="8736").balance)

    def test_final_invoice_with_previous_debit_and_credit(self):
        self.task.complete = 5
        self.task.save()

        partial_debit(self.project)
        partial_credit(self.project, Decimal(400)*Decimal(1.19))

        self.task.complete += 5
        self.task.save()
        final_debit(self.project)

        self.assertEquals(round(Decimal(560.00)*Decimal(1.19),2), self.project.account.balance)
        self.assertEquals(round(Decimal(960.00),2), Account.objects.get(code="8400").balance)
        self.assertEquals(round(Decimal(960.00)*Decimal(0.19),2), Account.objects.get(code="1776").balance)
        self.assertEquals(0, Account.objects.get(code="1718").balance)
        self.assertEquals(0, Account.objects.get(code="8736").balance)

    def test_final_invoice_with_previous_debit_and_discount_credit(self):
        self.task.complete = 5
        self.task.save()

        partial_debit(self.project)
        payment = Decimal(400)*Decimal(0.9)
        partial_credit(self.project, payment*Decimal(1.19), True)

        self.task.complete += 5
        self.task.save()
        final_debit(self.project)

        self.assertEquals(round(Decimal(560.00)*Decimal(1.19),2), self.project.account.balance)
        self.assertEquals(round(Decimal(960.00),2), Account.objects.get(code="8400").balance)
        self.assertEquals(round(payment*Decimal(0.19)+Decimal(560.00)*Decimal(0.19),2), Account.objects.get(code="1776").balance)
        self.assertEquals(0, Account.objects.get(code="1718").balance)
        self.assertEquals(Decimal(-40), Account.objects.get(code="8736").balance)