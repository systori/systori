from decimal import Decimal
from datetime import datetime
from django.test import TestCase
from django.utils.translation import activate

from ..company.factories import CompanyFactory
from ..user.factories import UserFactory
from ..project.factories import ProjectFactory
from ..task.factories import JobFactory, GroupFactory, TaskFactory, LineItemFactory
from ..directory.factories import ContactFactory

from ..timetracking.models import Timer
from systori.lib.accounting.tools import Amount

from . import type as pdf_type
from .models import Proposal, Invoice, Timesheet
from .factories import LetterheadFactory, DocumentTemplateFactory


class ProposalTests(TestCase):

    def setUp(self):
        activate('en')
        CompanyFactory()
        self.project = ProjectFactory()
        ContactFactory(
            project=self.project
        )
        self.letterhead = LetterheadFactory()
        self.job = JobFactory(project=self.project)
        self.group = GroupFactory(parent=self.job)
        self.task = TaskFactory(group=self.group)
        self.lineitem = LineItemFactory(task=self.task)

    def test_status_new(self):
        d = Proposal.objects.create(project=self.project, letterhead=self.letterhead)
        self.assertEquals('New', d.get_status_display())
        self.assertEquals(['Send'], [t.custom['label'] for t in d.get_available_status_transitions()])

    def test_status_sent(self):
        d = Proposal.objects.create(project=self.project, letterhead=self.letterhead)
        d.send()
        d.save()
        d = Proposal.objects.get(pk=d.pk)
        self.assertEquals('Sent', d.get_status_display())
        # TODO: for some reason result of get_available_status_transitions() is not consistently sorted
        labels = [str(t.custom['label']) for t in d.get_available_status_transitions()]
        labels.sort()
        self.assertEquals(['Approve', 'Decline'], labels)

    def test_serialize(self):
        proposal = Proposal.objects.create(project=self.project, letterhead=self.letterhead)
        proposal.json = {
            'jobs': [{'job': self.job}],
            'add_terms': False
        }
        pdf_type.proposal.serialize(proposal)
        self.maxDiff = None
        self.assertEqual({
            'add_terms': False,
            'jobs': [{
                'tasks': [],
                'groups': [{
                    'group.id': 2,
                    'code': '01.01',
                    'name': self.group.name,
                    'description': '',
                    'estimate': Decimal('0.0000'),
                    'groups': [],
                    'tasks': [{
                        'task.id': 1,
                        'code': '01.01.001',
                        'name': self.task.name,
                        'description': '',
                        'is_provisional': False,
                        'variant_group': None,
                        'variant_serial': 0,
                        'qty': Decimal('0.0000'),
                        'unit': '',
                        'price': Decimal('0.0000'),
                        'estimate': Decimal('0.0000'),
                        'lineitems': [{
                            'lineitem.id': 1,
                            'name': self.lineitem.name,
                            'price': Decimal('0.0000'),
                            'estimate': Decimal('0.0000'),
                            'qty': Decimal('0.0000'),
                            'unit': ''
                        }],
                    }],
                }],
            }],
        }, proposal.json)


class InvoiceTests(TestCase):

    def setUp(self):
        activate('en')
        CompanyFactory()
        self.project = ProjectFactory()
        ContactFactory(
            project=self.project
        )
        self.letterhead = LetterheadFactory()
        self.job = JobFactory(project=self.project)
        self.group = GroupFactory(parent=self.job)
        self.task = TaskFactory(group=self.group)
        self.lineitem = LineItemFactory(task=self.task)

    def test_serialize(self):
        invoice = Invoice.objects.create(project=self.project, letterhead=self.letterhead)
        invoice.json = {
            'jobs': [{'job': self.job}],
            'add_terms': False
        }
        pdf_type.invoice.serialize(invoice)
        self.maxDiff = None
        self.assertEqual({
            'jobs': [{
                'tasks': [],
                'groups': [{
                    'group.id': 2,
                    'code': '01.01',
                    'name': self.group.name,
                    'description': '',
                    'progress': Decimal('0.00'),
                    'estimate': Decimal('0.0000'),
                    'tasks': [{
                        'task.id': 1,
                        'code': '01.01.001',
                        'name': self.task.name,
                        'description': '',
                        'is_provisional': False,
                        'variant_group': None,
                        'variant_serial': 0,
                        'qty': Decimal('0.0000'),
                        'complete': Decimal('0.0000'),
                        'unit': '',
                        'price': Decimal('0.0000'),
                        'progress': Decimal('0.00'),
                        'estimate': Decimal('0.0000'),
                        'lineitems': [{
                            'lineitem.id': 1,
                            'name': self.lineitem.name,
                            'qty': Decimal('0.0000'),
                            'unit': '',
                            'price': Decimal('0.0000'),
                            'estimate': Decimal('0.0000'),
                        }],
                    }],
                    'groups': [],
                }],
            }],
            'add_terms': False,
            'debit': Amount.zero(),
            'invoiced': Amount.zero(),
            'paid': Amount.zero(),
            'unpaid': Amount.zero(),
            'payments': [],
            'job_debits': {}
        }, invoice.json)


class DocumentTemplateTests(TestCase):

    def setUp(self):
        CompanyFactory()
        self.project = ProjectFactory()
        ContactFactory(
            first_name='Ludwig',
            last_name='von Mises',
            project=self.project, is_billable=True
        )
        self.letterhead = LetterheadFactory()

    def test_render_english_tpl(self):
        activate('en')
        d = DocumentTemplateFactory(
            header="Dear [lastname]",
            footer="Thanks [firstname]!",
        )
        r = d.render(self.project)
        self.assertEqual("Dear von Mises", r['header'])
        self.assertEqual("Thanks Ludwig!", r['footer'])

    def test_render_german_tpl(self):
        activate('de')
        d = DocumentTemplateFactory(
            header="Dear [Nachname]",
            footer="Thanks [Vorname]!",
            document_type="invoice"
        )
        r = d.render(self.project)
        self.assertEqual("Dear von Mises", r['header'])
        self.assertEqual("Thanks Ludwig!", r['footer'])

    def test_render_sample_tpl(self):
        activate('en')
        d = DocumentTemplateFactory(
            header="Dear [lastname]",
            footer="Thanks [firstname]!",
            document_type="invoice"
        )
        r = d.render()
        self.assertEqual("Dear Smith", r['header'])
        self.assertEqual("Thanks John!", r['footer'])


class TimesheetTests(TestCase):

    def setUp(self):
        self.worker = UserFactory(company=CompanyFactory()).access.first()
        self.letterhead = LetterheadFactory()

    def test_generate(self):
        january = datetime(2017, 1, 9, 9)
        Timer.objects.create(
            worker=self.worker,
            start=january,
            end=january.replace(hour=18),
            kind=Timer.WORK
        )
        Timer.objects.create(
            worker=self.worker,
            start=january.replace(day=10),
            end=january.replace(day=10, hour=17),
            kind=Timer.HOLIDAY
        )
        sheet = Timesheet(
            document_date=january.replace(day=1),
            worker=self.worker,
            letterhead=self.letterhead
        )
        sheet.calculate()
        sheet.save()
        self.assertEqual(sheet.json['first_weekday'], 6)
        self.assertEqual(sheet.json['projects'][0]['days'][8], 9*60*60)
        self.assertEqual(sheet.json['projects'][0]['days'][9], 0)
        self.assertEqual(sheet.json['overtime'][8], 60*60)
        self.assertEqual(sheet.json['overtime'][9], 0)
        self.assertEqual(sheet.json['overtime_total'], 60*60)
        self.assertEqual(sheet.json['overtime_transferred'], 0)
        self.assertEqual(sheet.json['overtime_balance'], 60*60)
        self.assertEqual(sheet.json['holiday'][8], 0)
        self.assertEqual(sheet.json['holiday'][9], 8*60*60)
        self.assertEqual(sheet.json['holiday_total'], 8*60*60)
        self.assertEqual(sheet.json['holiday_transferred'], 0)
        self.assertEqual(sheet.json['holiday_added'], 2.5*8*60*60)
        self.assertEqual(sheet.json['holiday_balance'], 12*60*60)
        self.assertEqual(sheet.json['work'][8], 8*60*60)
        self.assertEqual(sheet.json['work'][9], 8*60*60)
        self.assertEqual(sheet.json['work_total'], 16*60*60)

        february = datetime(2017, 2, 6, 9)
        Timer.objects.create(
            worker=self.worker,
            start=february,
            end=february.replace(hour=18),
            kind=Timer.WORK
        )
        sheet = Timesheet(document_date=february, worker=self.worker, letterhead=self.letterhead)
        sheet.calculate()
        sheet.save()
        self.assertEqual(sheet.json['overtime_transferred'], 60*60)
        self.assertEqual(sheet.json['overtime_total'], 60*60)
        self.assertEqual(sheet.json['overtime_balance'], 2*60*60)
        self.assertEqual(sheet.json['holiday_transferred'], 12*60*60)
        self.assertEqual(sheet.json['holiday_added'], 2.5*8*60*60)
        self.assertEqual(sheet.json['holiday_total'], 0)
        self.assertEqual(sheet.json['holiday_balance'], 32*60*60)
