from decimal import Decimal as D
from django.test import TestCase
from ..accounting.test_workflow import create_data as create_accounting_data
from .forms import *


class InvoiceFormTests(TestCase):

    def setUp(self):
        create_accounting_data(self)
        self.task.complete = 5
        self.task.save()

        self.management_form = {}
        _management_form = InvoiceForm(instance=Invoice(project=self.project, json={'debits': []}),
                                       jobs=self.project.jobs.all()).management_form.initial
        for key, value in _management_form.items():
            self.management_form['job-'+key] = value

    def make_invoice_form(self, data):
        data.update(self.management_form)
        return InvoiceForm(data=data, instance=Invoice(project=self.project, json={'debits': []}),
                           jobs=self.project.jobs.all())

    def test_invoice_form_is_valid(self):
        form = self.make_invoice_form({

            'title': 'Invoice #1',
            'header': 'The Header',
            'footer': 'The Footer',
            'invoice_no': '2015/01/01',

            'job-0-is_invoiced': 'True',
            'job-0-job': self.job.id,
            'job-0-amount_net': '1',
            'job-0-amount_gross': '1',

            'job-1-is_invoiced': 'True',
            'job-1-job': self.job2.id,
            'job-1-amount_net': '1',
            'job-1-amount_gross': '1',

        })
        self.assertTrue(form.is_valid())
        self.assertEqual(D('2'), form.debit_net_total)
