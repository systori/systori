from decimal import Decimal as D
from django.test import TestCase

from systori.lib.testing import make_amount as A
from systori.lib.accounting.tools import Amount
from systori.apps.field.utils import days_ago

from ..company.factories import CompanyFactory
from ..project.factories import ProjectFactory
from ..task.factories import JobFactory

from .report import create_invoice_report, create_invoice_table
from .models import Entry, create_account_for_job
from .workflow import debit_jobs, credit_jobs, adjust_jobs, refund_jobs
from .workflow import create_chart_of_accounts
from .constants import TAX_RATE


class TestTransactionsTable(TestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.project = ProjectFactory()
        create_chart_of_accounts(self)

        jobs = []
        for i in range(5):
            job = JobFactory(project=self.project)
            job.account = create_account_for_job(job)
            job.save()
            jobs.append(job)

        self.job = jobs[0]
        self.job2 = jobs[1]
        self.job3 = jobs[2]
        self.job4 = jobs[3]
        self.job5 = jobs[4]

    def tbl(self, invoice_txn=None, jobs=None):
        if not invoice_txn:
            invoice_txn = debit_jobs([(self.job, A(0), Entry.WORK_DEBIT)], transacted_on=days_ago(0))
        if not jobs:
            jobs = [self.job]
        report = create_invoice_report(invoice_txn, jobs)
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

    def test_project_143_having_open_claim_2016_04_06(self):

        txn = debit_jobs([
            (self.job, Amount.from_net(D('22721.38'), TAX_RATE), Entry.WORK_DEBIT),
            (self.job2, Amount.from_net(D('3400.05'), TAX_RATE), Entry.WORK_DEBIT)
        ], transacted_on=days_ago(8))
        self.assertEqual(self.tbl(txn, [self.job, self.job2]), [
            ('',              'net',      'tax',     'gross'),
            ('progress', '26121.43',  '4963.07',  '31084.50'),
            ('debit',    '26121.43',  '4963.07',  '31084.50'),
        ])

        credit_jobs([
            (self.job, A('26227.29'), A('811.15'), A()),
            (self.job2, A('1572.71'), A('48.64'), A('2424.71')),
        ], D('27800.00'), transacted_on=days_ago(7))

        txn = debit_jobs([
            (self.job, Amount.from_net(D('8500'), TAX_RATE), Entry.WORK_DEBIT),
            (self.job2, Amount.from_net(D('4000'), TAX_RATE), Entry.WORK_DEBIT),
            (self.job3, Amount.from_net(D('1000'), TAX_RATE), Entry.WORK_DEBIT)
        ], transacted_on=days_ago(6))
        self.assertEqual(self.tbl(txn, [self.job, self.job2, self.job3]), [
            ('',              'net',      'tax',     'gross'),
            ('progress', '37583.86',  '7140.93',  '44724.79'),
            ('payment', '-23361.35', '-4438.65', '-27800.00'),
            ('discount',  '-722.51',  '-137.28',   '-859.79'),
            ('debit',    '13500.00',  '2565.00',  '16065.00'),
        ])

        credit_jobs([
            (self.job, A('9811.55'), A('303.45'), A()),
            (self.job2, A('3188.45'), A('98.61'), A('1472.94')),
        ], D('13000.00'), transacted_on=days_ago(5))

        txn = debit_jobs([
            (self.job2, Amount.from_net(D('11895.04'), TAX_RATE), Entry.WORK_DEBIT),
            (self.job3, Amount.from_net(D('1628.86'), TAX_RATE), Entry.WORK_DEBIT),
            (self.job4, Amount.from_net(D('358.31'), TAX_RATE), Entry.WORK_DEBIT)
        ], transacted_on=days_ago(4))
        self.assertEqual(self.tbl(txn, [self.job, self.job2, self.job3, self.job4]), [
            ('',              'net',      'tax',     'gross'),
            ('progress', '50228.31',  '9543.37',  '59771.68'),
            ('payment', '-23361.35', '-4438.65', '-27800.00'),
            ('discount',  '-722.51',  '-137.28',   '-859.79'),
            ('payment', '-10924.37', '-2075.63', '-13000.00'),
            ('discount',  '-337.87',   '-64.19',   '-402.06'),
            ('unpaid',   '-1000.00',  '-190.00',  '-1190.00'),
            ('debit',    '13882.21',  '2637.62',  '16519.83'),
        ])

        credit_jobs([
            (self.job2, A('6585.27'), A('203.67'), A('7366.16')),
            (self.job3, A('1938.34'), A('59.95'), A()),
            (self.job4, A('426.39'), A('13.19'), A()),
        ], D('8950.00'), transacted_on=days_ago(3))

        # Initial Case: Due to an underpaid job, invoice shows 'open claim'.

        dtxn = debit_jobs([
            (self.job2, Amount.from_net(D('17790.25'), TAX_RATE), Entry.WORK_DEBIT),
            (self.job5, Amount.from_net(D('6377.68'), TAX_RATE), Entry.WORK_DEBIT),
            (self.job3, Amount.from_net(D('2034.90'), TAX_RATE), Entry.WORK_DEBIT),
            (self.job4, Amount.from_net(D('716.62'), TAX_RATE), Entry.WORK_DEBIT)
        ], transacted_on=days_ago(1))
        self.assertEqual(self.tbl(dtxn, [self.job, self.job2, self.job3, self.job4, self.job5]), [
            ('',              'net',      'tax',     'gross'),
            ('progress', '70957.71', '13481.96',  '84439.67'),
            ('payment', '-23361.35', '-4438.65', '-27800.00'),
            ('discount',  '-722.51',  '-137.28',   '-859.79'),
            ('payment', '-10924.37', '-2075.63', '-13000.00'),
            ('discount',  '-337.87',   '-64.19',   '-402.06'),
            ('payment',  '-7521.01', '-1428.99',  '-8950.00'),
            ('discount',  '-232.61',   '-44.20',   '-276.81'),
            ('unpaid',    '-938.54',  '-178.32',  '-1116.86'),  # <-- open claim
            ('debit',    '26919.45',  '5114.70',  '32034.15'),
        ])
        dtxn.delete()

        # Adjusted Case: We adjust two jobs, no open claim, but progress is high due to over invoiced job.

        atxn = adjust_jobs([
            (self.job3, A(n='-949.62', t='-180.43')),
            (self.job4, A(n='11.08', t='2.11'))
        ], transacted_on=days_ago(1))

        dtxn = debit_jobs([
            (self.job2, Amount.from_net(D('17790.25'), TAX_RATE), Entry.WORK_DEBIT),
            (self.job5, Amount.from_net(D('6377.68'), TAX_RATE), Entry.WORK_DEBIT),
            (self.job3, Amount.from_net(D('2984.52'), TAX_RATE), Entry.WORK_DEBIT),
            (self.job4, Amount.from_net(D('705.54'), TAX_RATE), Entry.WORK_DEBIT)
        ], transacted_on=days_ago(3))
        self.assertEqual(self.tbl(dtxn, [self.job, self.job2, self.job3, self.job4, self.job5]), [
            ('',              'net',      'tax',     'gross'),
            ('progress', '70957.71', '13481.96',  '84439.67'),
            ('payment', '-23361.35', '-4438.65', '-27800.00'),
            ('discount',  '-722.51',  '-137.28',   '-859.79'),
            ('payment', '-10924.37', '-2075.63', '-13000.00'),
            ('discount',  '-337.87',   '-64.19',   '-402.06'),
            ('payment',  '-7521.01', '-1428.99',  '-8950.00'),
            ('discount',  '-232.61',   '-44.20',   '-276.81'),
            # ('unpaid',    '-938.54',  '-178.32',  '-1116.86'), <-- consumed into debit below
            ('debit',    '27857.99',  '5293.02',  '33151.01'),
        ])
        atxn.delete()
        dtxn.delete()

        # Adjusted Case II: We adjust three jobs, now invoice progress is correct and there is no open claim.

        atxn = adjust_jobs([
            (self.job, A(n='-4678.55', t='-888.92')),
            (self.job3, A(n='-949.62', t='-180.43')),
            (self.job4, A(n='11.08', t='2.11'))
        ], transacted_on=days_ago(1))

        dtxn = debit_jobs([
            (self.job2, Amount.from_net(D('17790.25'), TAX_RATE), Entry.WORK_DEBIT),
            (self.job5, Amount.from_net(D('6377.68'), TAX_RATE), Entry.WORK_DEBIT),
            (self.job3, Amount.from_net(D('2984.52'), TAX_RATE), Entry.WORK_DEBIT),
            (self.job4, Amount.from_net(D('705.54'), TAX_RATE), Entry.WORK_DEBIT)
        ], transacted_on=days_ago(3))
        self.assertEqual(self.tbl(dtxn, [self.job, self.job2, self.job3, self.job4, self.job5]), [
            ('',              'net',      'tax',     'gross'),
            ('progress', '66279.16', '12593.04',  '78872.20'),
            ('payment', '-23361.35', '-4438.65', '-27800.00'),
            ('discount',  '-722.51',  '-137.28',   '-859.79'),
            ('payment', '-10924.37', '-2075.63', '-13000.00'),
            ('discount',  '-337.87',   '-64.19',   '-402.06'),
            ('payment',  '-7521.01', '-1428.99',  '-8950.00'),
            ('discount',  '-232.61',   '-44.20',   '-276.81'),
            ('debit',    '27857.99',  '5293.02',  '33151.01'),
        ])
        atxn.delete()
        dtxn.delete()

        # Adjusted & Refund Case: We adjust three jobs as before but also issue a refund.
        #                         Just making sure refund does not change the invoice in anyway.

        atxn = adjust_jobs([
            (self.job, A(n='-4678.55', t='-888.92')),
            (self.job3, A(n='-949.62', t='-180.43')),
            (self.job4, A(n='11.08', t='2.11'))
        ], transacted_on=days_ago(1))

        rtxn = refund_jobs([
            (self.job, A(n='4678.55', t='888.92'), A()),
            (self.job2, A(), A(n='4678.55', t='888.92')),
        ], transacted_on=days_ago(1))

        dtxn = debit_jobs([
            (self.job2, Amount.from_net(D('17790.25'), TAX_RATE), Entry.WORK_DEBIT),
            (self.job5, Amount.from_net(D('6377.68'), TAX_RATE), Entry.WORK_DEBIT),
            (self.job3, Amount.from_net(D('2984.52'), TAX_RATE), Entry.WORK_DEBIT),
            (self.job4, Amount.from_net(D('705.54'), TAX_RATE), Entry.WORK_DEBIT)
        ], transacted_on=days_ago(3))
        self.assertEqual(self.tbl(dtxn, [self.job, self.job2, self.job3, self.job4, self.job5]), [
            ('',              'net',      'tax',     'gross'),
            ('progress', '66279.16', '12593.04',  '78872.20'),
            ('payment', '-23361.35', '-4438.65', '-27800.00'),
            ('discount',  '-722.51',  '-137.28',   '-859.79'),
            ('payment', '-10924.37', '-2075.63', '-13000.00'),
            ('discount',  '-337.87',   '-64.19',   '-402.06'),
            ('payment',  '-7521.01', '-1428.99',  '-8950.00'),
            ('discount',  '-232.61',   '-44.20',   '-276.81'),
            ('debit',    '27857.99',  '5293.02',  '33151.01'),
        ])
        atxn.delete()
        rtxn.delete()
        dtxn.delete()
