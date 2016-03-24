from decimal import Decimal as D
from django.test import TestCase
from systori.apps.field.utils import days_ago
from .report import create_invoice_report, create_invoice_table
from .models import Entry
from .workflow import debit_jobs, credit_jobs, adjust_jobs
from .test_workflow import create_data, A


class TestTransactionsTable(TestCase):
    def setUp(self):
        create_data(self)

    def tbl(self, invoice_txn=None):
        if not invoice_txn:
            invoice_txn = debit_jobs([(self.job, A(0), Entry.WORK_DEBIT)], transacted_on=days_ago(0))
        report = create_invoice_report(invoice_txn, [self.job])
        table = create_invoice_table(report)
        return [tuple(str(cell) for cell in row[:-1]) for row in table]

    def test_no_transactions(self):
        self.assertEqual(self.tbl(), [
            ('',          'net',  'tax', 'gross'),
            ('progress', '0.00', '0.00',  '0.00'),
            ('debit',    '0.00', '0.00',  '0.00'),
        ])

    def test_one_invoice_no_payment(self):
        txn = debit_jobs([(self.job, A(1190), Entry.WORK_DEBIT)])
        self.assertEqual(self.tbl(txn), [
            ('',             'net',    'tax',   'gross'),
            ('progress', '1000.00', '190.00', '1190.00'),
            ('debit',    '1000.00', '190.00', '1190.00'),
        ])

    def test_one_fully_paid_invoice(self):
        debit_jobs([(self.job, A(1190), Entry.WORK_DEBIT)], transacted_on=days_ago(2))
        credit_jobs([(self.job, A(1190), A(), A())], D(1190), transacted_on=days_ago(1))
        self.assertEqual(self.tbl(), [
            ('',             'net',     'tax',    'gross'),
            ('progress', '1000.00',  '190.00',  '1190.00'),
            ('payment', '-1000.00', '-190.00', '-1190.00'),
            ('debit',    '0.00',       '0.00',     '0.00'),
        ])

    def test_one_partially_paid_invoice(self):
        debit_jobs([(self.job, A(1190), Entry.WORK_DEBIT)], transacted_on=days_ago(2))
        credit_jobs([(self.job, A(595), A(), A())], D(595), transacted_on=days_ago(1))
        self.assertEqual(self.tbl(), [
            ('',             'net',    'tax',   'gross'),
            ('progress', '1000.00', '190.00', '1190.00'),
            ('payment',  '-500.00', '-95.00', '-595.00'),
            ('unpaid',   '-500.00', '-95.00', '-595.00'),
            ('debit',       '0.00',   '0.00',    '0.00'),
        ])

    def test_one_invoice_paid_with_adjustment(self):
        debit_jobs([(self.job, A(1190), Entry.WORK_DEBIT)], transacted_on=days_ago(2))
        credit_jobs([(self.job, A(595), A(), A(595))], D(595), transacted_on=days_ago(1))
        self.assertEqual(self.tbl(), [
            ('',            'net',    'tax',   'gross'),
            ('progress', '500.00',  '95.00',  '595.00'),
            ('payment', '-500.00', '-95.00', '-595.00'),
            ('debit',       '0.00',   '0.00',    '0.00'),
        ])

    def test_one_invoice_paid_with_discount(self):
        debit_jobs([(self.job, A(1190), Entry.WORK_DEBIT)], transacted_on=days_ago(2))
        credit_jobs([(self.job, A(595), A(595), A())], D(595), transacted_on=days_ago(1))
        self.assertEqual(self.tbl(), [
            ('',             'net',    'tax',   'gross'),
            ('progress', '1000.00', '190.00', '1190.00'),  # discount does not reduced the progress
            ('payment',  '-500.00', '-95.00', '-595.00'),  # invoice is not shown because it was 'fully paid'
            ('discount', '-500.00', '-95.00', '-595.00'),  # discount shown
            ('debit',       '0.00',   '0.00',    '0.00'),
        ])

    def test_one_invoice_paid_with_discount_and_adjustment(self):
        debit_jobs([(self.job, A(1190), Entry.WORK_DEBIT)], transacted_on=days_ago(2))
        credit_jobs([(self.job, A(595), A(297.50), A(297.50))], D(595), transacted_on=days_ago(1))
        self.assertEqual(self.tbl(), [
            ('',             'net',    'tax',   'gross'),
            ('progress',  '750.00', '142.50', '892.50'),  # progress reduced by adjustment
            ('payment',  '-500.00', '-95.00', '-595.00'),  # invoice is not shown because it was 'fully paid'
            ('discount', '-250.00', '-47.50', '-297.50'),  # also we have a discount
            ('debit',       '0.00',   '0.00',    '0.00'),
        ])

    def test_one_invoice_with_adjustment_and_unpaid_portion(self):
        debit_jobs([(self.job, A(1019), Entry.WORK_DEBIT)], transacted_on=days_ago(2))
        adjust_jobs([(self.job, A(-900))], transacted_on=days_ago(1))
        self.assertEqual(self.tbl(), [
            ('',             'net',    'tax',   'gross'),
            ('progress',  '100.00',  '19.00',  '119.00'),  # progress reduced by adjustment
            ('unpaid',   '-100.00', '-19.00', '-119.00'),  # reduced invoice is shown
            ('debit',       '0.00',   '0.00',    '0.00'),
        ])

    def test_invoices_with_adjustment_and_payment_project_41_issue_2016_02_24(self):
        debit_jobs([(self.job, A(1190), Entry.WORK_DEBIT)], transacted_on=days_ago(6))
        credit_jobs([(self.job, A(1190), A(0), A(0))], D(1190), transacted_on=days_ago(5))

        debit_jobs([(self.job, A(1019), Entry.WORK_DEBIT)], transacted_on=days_ago(4))
        adjust_jobs([(self.job, A(-900))], transacted_on=days_ago(3))
        credit_jobs([(self.job, A(119), A(0), A(0))], D(119), transacted_on=days_ago(2))

        txn = debit_jobs([(self.job, A(119), Entry.WORK_DEBIT)], transacted_on=days_ago(1))

        self.assertEqual(self.tbl(txn), [
            ('',             'net',    'tax',   'gross'),
            ('progress',  '1200.00',  '228.00',  '1428.00'),
            ('payment',  '-1000.00', '-190.00', '-1190.00'),
            ('payment',  '-100.00', '-19.00', '-119.00'),
            ('debit',     '100.00',  '19.00', '119.00'),
        ])

    def test_project_150_issue_2016_01_17(self):
        debit_jobs([(self.job, A(28560), Entry.WORK_DEBIT)], transacted_on=days_ago(4))
        debit_jobs([(self.job, A(10569.95), Entry.WORK_DEBIT)], transacted_on=days_ago(3))
        debit_jobs([(self.job, A(14045.95), Entry.WORK_DEBIT)], transacted_on=days_ago(2))

        credit_jobs([(self.job, A(28560), A(0), A(0))], D(28560), transacted_on=days_ago(3))
        credit_jobs([(self.job, A(8925), A(0), A(1644.95))], D(8925), transacted_on=days_ago(2))

        self.assertEqual(self.tbl(), [
            ('',               'net',      'tax',     'gross'),
            ('progress',  '43303.32',  '8227.63',  '51530.95'),
            ('payment',  '-24000.00', '-4560.00', '-28560.00'),
            ('payment',   '-7500.00', '-1425.00',  '-8925.00'),
            ('unpaid',   '-11803.32', '-2242.63', '-14045.95'),
            ('debit',         '0.00',     '0.00',      '0.00'),
        ])

    def test_two_invoices_no_payment(self):
        debit_jobs([(self.job, A(1190), Entry.WORK_DEBIT)])
        txn = debit_jobs([(self.job, A(1190), Entry.WORK_DEBIT)])
        self.assertEqual(self.tbl(txn), [
            ('',             'net',     'tax',    'gross'),
            ('progress', '2000.00',  '380.00',  '2380.00'),
            ('unpaid',  '-1000.00', '-190.00', '-1190.00'),
            ('debit',    '1000.00',  '190.00',  '1190.00'),
        ])

    def test_two_invoices_with_tiny_payment(self):
        debit_jobs([(self.job, A(1190), Entry.WORK_DEBIT)], transacted_on=days_ago(3))
        debit_jobs([(self.job, A(1190), Entry.WORK_DEBIT)], transacted_on=days_ago(2))
        credit_jobs([(self.job, A(119), A(), A())], D(119), transacted_on=days_ago(1))
        self.assertEqual(self.tbl(), [
            ('',             'net',     'tax',    'gross'),
            ('progress', '2000.00',  '380.00',  '2380.00'),
            ('payment',  '-100.00',  '-19.00',  '-119.00'),
            ('unpaid',  '-1900.00', '-361.00', '-2261.00'),
            ('debit',       '0.00',    '0.00',     '0.00'),
        ])

    def test_two_invoices_with_one_fully_paid(self):
        debit_jobs([(self.job, A(1190), Entry.WORK_DEBIT)], transacted_on=days_ago(3))
        debit_jobs([(self.job, A(1190), Entry.WORK_DEBIT)], transacted_on=days_ago(2))
        credit_jobs([(self.job, A(1190), A(), A())], D(1190), transacted_on=days_ago(1))
        self.assertEqual(self.tbl(), [
            ('',             'net',     'tax',    'gross'),
            ('progress', '2000.00',  '380.00',  '2380.00'),
            ('payment', '-1000.00', '-190.00', '-1190.00'),
            ('unpaid',  '-1000.00', '-190.00', '-1190.00'),
            ('debit',       '0.00',    '0.00',     '0.00')
        ])

    def test_two_invoices_both_fully_paid(self):
        debit_jobs([(self.job, A(1190), Entry.WORK_DEBIT)], transacted_on=days_ago(3))
        debit_jobs([(self.job, A(1190), Entry.WORK_DEBIT)], transacted_on=days_ago(2))
        credit_jobs([(self.job, A(2380), A(), A())], D(2380), transacted_on=days_ago(1))
        self.assertEqual(self.tbl(), [
            ('',             'net',     'tax',    'gross'),
            ('progress', '2000.00',  '380.00',  '2380.00'),
            ('payment', '-2000.00', '-380.00', '-2380.00'),
            ('debit',       '0.00',    '0.00',     '0.00')
        ])
