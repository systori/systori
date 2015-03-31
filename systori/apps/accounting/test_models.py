from decimal import Decimal
from django.test import TestCase
from ..task.test_models import create_task_data
from ..project.models import Project
from .models import *


def create_data(self):
    create_task_data(self)
    Account.objects.create(project=self.project)
    self.project = Project.objects.get(id=self.project.id)


class TestInitialInvoice(TestCase):

    def setUp(self):
        create_data(self)

    def test_no_billable_tasks(self):
        self.assertEquals(0, self.project.billable_total)
        self.assertEquals(0, self.project.account.balance)
        self.assertEquals([], list(self.project.billable_jobs))

    def test_billable_tasks(self):
        self.task.complete = 5
        self.task.save()
        self.assertEquals(Decimal(480), self.project.billable_total)
        self.assertEquals(1, len(list(self.project.billable_jobs)))

    def test_invoice_account(self):
        pass

class TestSubsequentInvoice(TestCase):

    def setUp(self):
        create_data(self)
        amount = self.project.billable_total
        self.project.account.invoice(amount)

    def test_no_billable_tasks(self):
        self.assertEquals(0, self.project.billable_total)
        self.assertEquals([], list(self.project.billable_jobs))

    def test_billable_tasks(self):
        self.task.complete = 5
        self.task.save()
        self.assertEquals(Decimal(480), self.project.billable_total)
        self.assertEquals(1, len(list(self.project.billable_jobs)))