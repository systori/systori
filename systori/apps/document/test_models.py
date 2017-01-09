from datetime import date
from decimal import Decimal
from django.test import TestCase
from django.utils.translation import activate

from ..company.factories import CompanyFactory
from ..project.factories import ProjectFactory
from ..project.models import Project
from ..task.factories import JobFactory, GroupFactory, TaskFactory, LineItemFactory
from ..task.models import Job, Group, Task
from ..directory.factories import ContactFactory

from systori.lib.accounting.tools import Amount

from . import type as pdf_type
from .models import Proposal, Invoice
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
                'taskgroups': [{
                    'id': 2, 'code': '01.01',
                    'name': self.group.name,
                    'description': '',
                    'estimate_net': Decimal('0.0000'),
                    'taskgroups': [],
                    'tasks': [{
                        'id': 1, 'code': '01.01.001',
                        'name': self.task.name,
                        'price': Decimal('0.0000'),
                        'qty': Decimal('0.0000'),
                        'unit': '',
                        'description': '',
                        'estimate_net': Decimal('0.0000'),
                        'is_optional': False,
                        'lineitems': [{
                            'id': 1,
                            'name': self.lineitem.name,
                            'price': Decimal('0.0000'),
                            'price_per': Decimal('0.0000'),
                            'qty': Decimal('0.0000'),
                            'unit': ''
                        }],
                    }],
                    'id': 2,'job_id':self.job.job_id, 'code': '01.01',
                    'name': self.group.name,
                    'description': '',
                    'estimate_net': Decimal('0.0000'),

                }],
                'tasks': []
            }],
        }, proposal.json)

    def test_render_small_project(self):
        small_project = ProjectFactory(structure="01.0001")
        ContactFactory(
            project=small_project
        )
        job = JobFactory(project=small_project)
        task = TaskFactory(group=job)
        lineitem = LineItemFactory(task=task)
        project = Project.objects.with_estimate().get(pk=small_project.pk)
        proposal = Proposal.objects.create(project=project, letterhead=self.letterhead)
        proposal.json = {
            'jobs': [{'job': self.job}],
            'add_terms': False
        }
        pdf_type.proposal.serialize(proposal)
        proposal.json['business'] = 'testBusiness'
        proposal.json['salutation'] = project.project_contacts.first().contact.salutation
        proposal.json['first_name'] = project.project_contacts.first().contact.first_name
        proposal.json['last_name'] = project.project_contacts.first().contact.first_name
        proposal.json['address'] = project.project_contacts.first().contact.address
        proposal.json['postal_code'] = project.project_contacts.first().contact.postal_code
        proposal.json['city'] = project.project_contacts.first().contact.city
        proposal.json['document_date'] = date.today().isoformat()
        proposal.json['title'] = 'testProposal'
        proposal.json['header'] = 'dear sir or madam'
        proposal.json['footer'] = 'bye'
        proposal.json['estimate_total'] = Amount.from_gross(project.estimate, Decimal('0.19'))
        file = pdf_type.proposal.render(proposal.json, self.letterhead, False, 'print')
        f = open('test_small.pdf', 'wb+')
        f.write(file)
        f.close()

    def test_render_big_project(self):
        project = ProjectFactory(structure="0.00.00.00.00.0000")
        job = JobFactory(project=project)  # type: Job
        #job.generate_groups()

        group = GroupFactory(parent=job)  # type: Group
        #group.generate_groups()


        proposal = Proposal.objects.create(project=project, letterhead=self.letterhead)
        proposal.json = {
            'jobs': [{'job': self.job}],
            'add_terms': False
        }
        pdf_type.proposal.serialize(proposal)
        proposal.json['business'] = 'testBusiness'
        proposal.json['salutation'] = project.project_contacts.first().contact.salutation
        proposal.json['first_name'] = project.project_contacts.first().contact.first_name
        proposal.json['last_name'] = project.project_contacts.first().contact.first_name
        proposal.json['address'] = project.project_contacts.first().contact.address
        proposal.json['postal_code'] = project.project_contacts.first().contact.postal_code
        proposal.json['city'] = project.project_contacts.first().contact.city
        proposal.json['document_date'] = date.today().isoformat()
        proposal.json['title'] = 'testProposal'
        proposal.json['header'] = 'dear sir or madam'
        proposal.json['footer'] = 'bye'
        proposal.json['estimate_total'] = Amount.from_gross(project.estimate, Decimal('0.19'))
        file = pdf_type.proposal.render(proposal.json, self.letterhead, False, 'print')
        f = open('test_big.pdf', 'wb+')
        f.write(file)
        f.close()


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
                'taskgroups': [{
                    'id': 2, 'code': '01.01',
                    'name': self.group.name,
                    'description': '',
                    'total': Decimal('0.00'),
                    'tasks': [{
                        'id': 1, 'code': '01.01.001',
                        'name': self.task.name,
                        'price': Decimal('0.0000'),
                        'total': Decimal('0.00'),
                        'unit': '',
                        'description': '',
                        'complete': Decimal('0.0000'),
                        'lineitems': [{
                            'id': 1,
                            'name': self.lineitem.name,
                            'price': Decimal('0.0000'),
                            'price_per': Decimal('0.0000'),
                            'qty': Decimal('0.0000'),
                            'unit': ''
                        }],
                    }],
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
