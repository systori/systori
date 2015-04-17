from decimal import Decimal
from django.test import TestCase
from ..task.test_models import create_task_data
from ..project.models import Project
from .models import *
from .skr03 import *


def create_data(self):
    create_task_data(self)
    create_chart_of_accounts(self)
    self.project.account = Account.objects.create(account_type=Account.ASSET, code='1{:04}'.format(self.project.id))
    self.project.save()

def tgrp():
    return TransactionGroup.objects.create()


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
        partial_debit(tgrp(), self.project)
        self.assertEquals(round(Decimal(480.00)*Decimal(1.19),2), self.project.account.balance)
        self.assertEquals(round(Decimal(480.00)*Decimal(1.19),2), Account.objects.get(code="1710").balance)

    def test_initial_partial_debit_with_prepayment(self):
        self.task.complete += 2
        self.task.save()
        partial_credit(tgrp(), [(self.project, Decimal(480.00)*Decimal(1.19), False)], Decimal(480.00)*Decimal(1.19))
        partial_debit(tgrp(), self.project)
        self.assertEquals(round(Decimal(192.0)*Decimal(1.19),2), self.project.account.balance)


class TestPartialCredit(TestCase):

    EXPECTED_BALANCE = round(Decimal(480.00)*Decimal(1.19)-Decimal(400),2)

    def setUp(self):
        create_data(self)
        self.task.complete = 5
        self.task.save()
        partial_debit(tgrp(), self.project)

    def test_partial_credit(self):
        partial_credit(tgrp(), [(self.project, Decimal(400), False)], Decimal(400))
        self.assertEquals(self.EXPECTED_BALANCE, self.project.account.balance)
        self.assertEquals(self.EXPECTED_BALANCE, Account.objects.get(code="1710").balance)
        self.assertEquals(round(Decimal(400)/Decimal(1.19),2), Account.objects.get(code="1718").balance)
        self.assertEquals(round(Decimal(400)/Decimal(1.19)*Decimal(.19),2), Account.objects.get(code="1776").balance)

    def test_partial_credit_w_discount(self):
        # different payment amount but ending balances are the same because discount was applied
        partial_credit(tgrp(), [(self.project, Decimal(360), True)], Decimal(360))
        self.assertEquals(self.EXPECTED_BALANCE, self.project.account.balance)
        self.assertEquals(self.EXPECTED_BALANCE, Account.objects.get(code="1710").balance)
        self.assertEquals(round(Decimal(360)/Decimal(1.19),2), Account.objects.get(code="1718").balance)
        self.assertEquals(round(Decimal(360)/Decimal(1.19)*Decimal(.19),2), Account.objects.get(code="1776").balance)

    def test_partial_credit_in_full(self):
        partial_credit(tgrp(), [(self.project, Decimal(480)*Decimal(1.19), False)], Decimal(480)*Decimal(1.19))
        self.assertEquals(Decimal(0), self.project.account.balance)
        self.assertEquals(Decimal(0), Account.objects.get(code="1710").balance)
        self.assertEquals(round(Decimal(480),2), Account.objects.get(code="1718").balance)
        self.assertEquals(round(Decimal(480)*Decimal(.19),2), Account.objects.get(code="1776").balance)

    def test_partial_credit_in_full_w_discount(self):
        # different payment amount but ending balance is still 0 because discount was applied
        partial_credit(tgrp(), [(self.project, Decimal(432)*Decimal(1.19), True)], Decimal(432)*Decimal(1.19))
        self.assertEquals(Decimal(0), self.project.account.balance)
        self.assertEquals(Decimal(0), Account.objects.get(code="1710").balance)
        self.assertEquals(round(Decimal(432),2), Account.objects.get(code="1718").balance)
        self.assertEquals(round(Decimal(432)*Decimal(.19),2), Account.objects.get(code="1776").balance)


class TestMultiAccountPartialCredit(TestCase):

    EXPECTED_BALANCE = round(Decimal(480.00)*Decimal(1.19)-Decimal(400),2)

    def setUp(self):

        create_data(self)
        self.task.complete = 5
        self.task.save()

        self2 = type('',(),{})()
        create_task_data(self2, False)
        self2.project.account = Account.objects.create(account_type=Account.ASSET, code='1{:04}'.format(self2.project.id))
        self2.project.save()
        self2.task.complete = 5
        self2.task.save()

        self.project2 = self2.project
        partial_debit(tgrp(), self.project)
        partial_debit(tgrp(), self.project2)

    def test_multi_partial_credit_w_discount(self):
        self.assertEquals(round(Decimal(480)*Decimal(1.19),2), self.project.account.balance)
        self.assertEquals(round(Decimal(480)*Decimal(1.19),2), self.project2.account.balance)
        self.assertEquals(round(Decimal(960)*Decimal(1.19),2), Account.objects.get(code="1710").balance)
        partial_credit(tgrp(), [
            (self.project, Decimal(480)*Decimal(1.19), False),
            (self.project2, Decimal(432)*Decimal(1.19), True)
        ], Decimal(480)*Decimal(1.19) + Decimal(432)*Decimal(1.19))
        self.assertEquals(Decimal(0), self.project.account.balance)
        self.assertEquals(Decimal(0), self.project2.account.balance)
        self.assertEquals(Decimal(0), Account.objects.get(code="1710").balance)
        self.assertEquals(round(Decimal(912),2), Account.objects.get(code="1718").balance)
        self.assertEquals(round(Decimal(912)*Decimal(.19),2), Account.objects.get(code="1776").balance)


class TestSubsequentDebit(TestCase):

    def setUp(self):
        create_data(self)

        self.task.complete = 5
        self.task.save()
        partial_debit(tgrp(), self.project) # first invoice
        partial_credit(tgrp(), [(self.project, Decimal(480)*Decimal(1.19), False)], Decimal(480)*Decimal(1.19)) # a full payment

        self.task.complete += 2
        self.task.save()

    def test_subsequent_partial_debit(self):
        self.assertEquals(Decimal(0), self.project.account.balance)
        partial_debit(tgrp(), self.project)
        self.assertEquals(round(Decimal(192.0)*Decimal(1.19),2), self.project.account.balance)


class TestFinalDebit(TestCase):

    def setUp(self):
        create_data(self)

    def test_final_debit_no_previous_debits_or_credits(self):
        self.task.complete = 10
        self.task.save()
        final_debit(tgrp(), self.project)

        self.assertEquals(round(Decimal(960.00)*Decimal(1.19),2), self.project.account.balance)
        self.assertEquals(round(Decimal(960.00),2), Account.objects.get(code="8400").balance)
        self.assertEquals(round(Decimal(960.00)*Decimal(0.19),2), Account.objects.get(code="1776").balance)
        self.assertEquals(0, Account.objects.get(code="1718").balance)

    def test_final_invoice_with_previous_debit(self):
        self.task.complete = 5
        self.task.save()
        partial_debit(tgrp(), self.project)

        self.task.complete += 5
        self.task.save()
        final_debit(tgrp(), self.project)

        self.assertEquals(round(Decimal(960.00)*Decimal(1.19),2), self.project.account.balance)
        self.assertEquals(round(Decimal(960.00),2), Account.objects.get(code="8400").balance)
        self.assertEquals(round(Decimal(960.00)*Decimal(0.19),2), Account.objects.get(code="1776").balance)
        self.assertEquals(0, Account.objects.get(code="1718").balance)

    def test_final_invoice_with_previous_debit_and_credit(self):
        self.task.complete = 5
        self.task.save()

        partial_debit(tgrp(), self.project)
        partial_credit(tgrp(), [(self.project, Decimal(400)*Decimal(1.19), False)], Decimal(400)*Decimal(1.19))

        self.task.complete += 5
        self.task.save()
        final_debit(tgrp(), self.project)

        self.assertEquals(round(Decimal(560.00)*Decimal(1.19),2), self.project.account.balance)
        self.assertEquals(round(Decimal(960.00),2), Account.objects.get(code="8400").balance)
        self.assertEquals(round(Decimal(960.00)*Decimal(0.19),2), Account.objects.get(code="1776").balance)
        self.assertEquals(0, Account.objects.get(code="1718").balance)

    def test_final_invoice_with_previous_debit_and_discount_credit(self):
        self.task.complete = 5
        self.task.save()

        partial_debit(tgrp(), self.project)
        payment = Decimal(400)*Decimal(0.9)
        partial_credit(tgrp(), [(self.project, payment*Decimal(1.19), True)], payment*Decimal(1.19))

        self.task.complete += 5
        self.task.save()
        final_debit(tgrp(), self.project)

        self.assertEquals(round(Decimal(560.00)*Decimal(1.19),2), self.project.account.balance)
        self.assertEquals(round(Decimal(920.00),2), Account.objects.get(code="8400").balance)
        self.assertEquals(round(payment*Decimal(0.19)+Decimal(560.00)*Decimal(0.19),2), Account.objects.get(code="1776").balance)
        self.assertEquals(0, Account.objects.get(code="1718").balance)
