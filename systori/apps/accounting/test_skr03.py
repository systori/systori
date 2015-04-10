from decimal import Decimal
from django.test import TestCase
from ..task.test_models import create_task_data
from ..project.models import Project
from .models import *
from .skr03 import *


def create_data(self):
    create_task_data(self)

    self.project.account = Account.objects.create(account_type=Account.ASSET, code="10001")
    self.project.save()

    self.promised_payments = Account.objects.create(account_type=Account.LIABILITY, code="1710")
    self.partial_payments = Account.objects.create(account_type=Account.LIABILITY, code="1718")
    self.tax_payments = Account.objects.create(account_type=Account.LIABILITY, code="1776")

    self.bank = Account.objects.create(account_type=Account.ASSET, code="1200")

    self.income = Account.objects.create(account_type=Account.INCOME, code="8400")

    self.project = Project.objects.get(id=self.project.id)


class TestInitialInvoice(TestCase):

    def setUp(self):
        create_data(self)
        self.task.complete = 5
        self.task.save()

    def test_zero_balance(self):
        self.assertEquals(0, self.project.account.balance)

    def test_billable_tasks(self):
        self.assertEquals(Decimal(480), self.project.billable_total)
        self.assertEquals(1, len(list(self.project.billable_jobs)))

    def test_partial_invoice_created(self):
        partial_invoice(self.project)
        self.assertEquals(round(Decimal(480.00)*Decimal(1.19),2), self.project.account.balance)


class TestPartialPayment(TestCase):

    def setUp(self):
        create_data(self)
        self.task.complete = 5
        self.task.save()
        partial_invoice(self.project)

    def test_partial_payment_made(self):
        invoiced = round(Decimal(480.00)*Decimal(1.19),2)
        partial_payment(self.project, 400)
        self.assertEquals(invoiced-400, self.project.account.balance)


class TestFinalInvoice(TestCase):

    def setUp(self):
        create_data(self)
        self.task.complete = 5
        self.task.save()
        partial_invoice(self.project)
        partial_payment(self.project, 400)
    
    def test_final_invoice_created(self):
        final_invoice(self.project)
        invoiced = round(Decimal(480.00)*Decimal(1.19),2)-400
        self.assertEquals(round(Decimal(480.00)*Decimal(1.19),2), self.project.account.balance)