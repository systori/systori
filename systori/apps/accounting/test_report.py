from decimal import Decimal as D
from django.test import TestCase
from systori.apps.field.utils import days_ago
from .report import get_transaction_report, generate_transaction_table
from .models import Entry
from .workflow import debit_jobs, credit_jobs
from .test_workflow import create_data


class TestTransactionsTable(TestCase):
    def setUp(self):
        create_data(self)

    def tbl(self):
        txns = get_transaction_report([self.job])
        table = generate_transaction_table(txns)
        return [tuple(str(cell) for cell in row[:-1]) for row in table]

    def test_no_transactions(self):
        self.assertEqual(self.tbl(), [
            ('',          'net',  'tax','gross'),
            ('progress', '0.00', '0.00', '0.00'),
        ])

    def test_one_invoice_no_payment(self):
        debit_jobs([(self.job, D(1190.00), Entry.WORK_DEBIT)])
        self.assertEqual(self.tbl(), [
            ('',             'net',     'tax',    'gross'),
            ('progress', '1000.00',  '190.00',  '1190.00'),
            ('invoice', '-1000.00', '-190.00', '-1190.00'),
        ])

    def test_one_fully_paid_invoice(self):
        debit_jobs([(self.job, D(1190.00), Entry.WORK_DEBIT)], transacted_on=days_ago(2))
        credit_jobs([(self.job, D(1190.00), 0, 0)], D(1190.00), transacted_on=days_ago(1))
        self.assertEqual(self.tbl(), [
            ('',             'net',     'tax',    'gross'),
            ('progress', '1000.00',  '190.00',  '1190.00'),
            ('payment', '-1000.00', '-190.00', '-1190.00'),  # payment hides the fully paid invoice
        ])

    def test_one_partially_paid_invoice(self):
        debit_jobs([(self.job, D(1190.00), Entry.WORK_DEBIT)], transacted_on=days_ago(2))
        credit_jobs([(self.job, D(595.00), 0, 0)], D(595.00), transacted_on=days_ago(1))
        self.assertEqual(self.tbl(), [
            ('',             'net',    'tax',   'gross'),
            ('progress', '1000.00', '190.00', '1190.00'),
            ('invoice',  '-500.00', '-95.00', '-595.00'),  # showing how much of the invoice is still unpaid
            ('payment',  '-500.00', '-95.00', '-595.00'),
        ])

    def test_one_invoice_paid_with_adjustment(self):
        debit_jobs([(self.job, D(1190.00), Entry.WORK_DEBIT)], transacted_on=days_ago(2))
        credit_jobs([(self.job, D(595.00), 0, D(595.00))], D(595.00), transacted_on=days_ago(1))
        self.assertEqual(self.tbl(), [
            ('',            'net',    'tax',   'gross'),
            ('progress', '500.00',  '95.00',  '595.00'),  # adjustment reduces the progress
            ('payment', '-500.00', '-95.00', '-595.00'),  # invoice is not shown because it was 'fully paid'
        ])

    def test_one_invoice_paid_with_discount(self):
        debit_jobs([(self.job, D(1190.00), Entry.WORK_DEBIT)], transacted_on=days_ago(2))
        credit_jobs([(self.job, D(595.00), D(595.00), 0)], D(595.00), transacted_on=days_ago(1))
        self.assertEqual(self.tbl(), [
            ('',             'net',    'tax',   'gross'),
            ('progress', '1000.00', '190.00', '1190.00'),  # discount does not reduced the progress
            ('payment',  '-500.00', '-95.00', '-595.00'),  # invoice is not shown because it was 'fully paid'
            ('discount', '-500.00', '-95.00', '-595.00'),  # discount shown
        ])

    def test_one_invoice_paid_with_discount_and_adjustment(self):
        debit_jobs([(self.job, D(1190.00), Entry.WORK_DEBIT)], transacted_on=days_ago(2))
        credit_jobs([(self.job, D(595.00), D(297.50), D(297.50))], D(595.00), transacted_on=days_ago(1))
        self.assertEqual(self.tbl(), [
            ('',             'net',    'tax',   'gross'),
            ('progress',  '750.00', '142.50', '892.50'),  # progress reduced by adjustment
            ('payment',  '-500.00', '-95.00', '-595.00'),  # invoice is not shown because it was 'fully paid'
            ('discount', '-250.00', '-47.50', '-297.50'),  # also we have a discount
        ])

    def test_two_invoices_no_payment(self):
        debit_jobs([(self.job, D(1190.00), Entry.WORK_DEBIT)])
        debit_jobs([(self.job, D(1190.00), Entry.WORK_DEBIT)])
        self.assertEqual(self.tbl(), [
            ('',             'net',     'tax',    'gross'),
            ('progress', '2000.00',  '380.00',  '2380.00'),
            ('invoice', '-1000.00', '-190.00', '-1190.00'),
            ('invoice', '-1000.00', '-190.00', '-1190.00'),
        ])

    def test_two_invoices_with_tiny_payment(self):
        debit_jobs([(self.job, D(1190.00), Entry.WORK_DEBIT)], transacted_on=days_ago(3))
        debit_jobs([(self.job, D(1190.00), Entry.WORK_DEBIT)], transacted_on=days_ago(2))
        credit_jobs([(self.job, D(119.00), 0, 0)], D(119.00), transacted_on=days_ago(1))
        self.assertEqual(self.tbl(), [
            ('',             'net',     'tax',    'gross'),
            ('progress', '2000.00',  '380.00',  '2380.00'),
            ('invoice',  '-900.00', '-171.00', '-1071.00'),  # this invoice reduced by 119 payment, auto pay algorithm
            ('invoice', '-1000.00', '-190.00', '-1190.00'),
            ('payment',  '-100.00',  '-19.00',  '-119.00'),
        ])

    def test_two_invoices_with_one_fully_paid(self):
        debit_jobs([(self.job, D(1190.00), Entry.WORK_DEBIT)], transacted_on=days_ago(3))
        debit_jobs([(self.job, D(1190.00), Entry.WORK_DEBIT)], transacted_on=days_ago(2))
        credit_jobs([(self.job, D(1190.00), 0, 0)], D(1190.00), transacted_on=days_ago(1))
        self.assertEqual(self.tbl(), [
            ('',             'net',     'tax',    'gross'),
            ('progress', '2000.00',  '380.00',  '2380.00'),
            ('invoice', '-1000.00', '-190.00', '-1190.00'),  # one of the invoices is hidden because it's fully paid
            ('payment', '-1000.00', '-190.00', '-1190.00'),
        ])

    def test_two_invoices_both_fully_paid(self):
        debit_jobs([(self.job, D(1190.00), Entry.WORK_DEBIT)], transacted_on=days_ago(3))
        debit_jobs([(self.job, D(1190.00), Entry.WORK_DEBIT)], transacted_on=days_ago(2))
        credit_jobs([(self.job, D(2380.00), 0, 0)], D(2380.00), transacted_on=days_ago(1))
        self.assertEqual(self.tbl(), [
            ('',             'net',     'tax',    'gross'),
            ('progress', '2000.00',  '380.00',  '2380.00'),
            ('payment', '-2000.00', '-380.00', '-2380.00'),  # both invoices are hidden because they're both fully paid
        ])
