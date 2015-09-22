from datetime import timedelta, date
from decimal import Decimal

from django.test import TestCase, Client
from django.utils import timezone
from django.core.urlresolvers import reverse

from ..accounting.test_skr03 import create_data
from ..accounting.skr03 import partial_credit, partial_debit
from ..directory.models import Contact, ProjectContact
from .models import Proposal, Invoice
from .views import ProposalUpdate


class DocumentTestCase(TestCase):

    def setUp(self):
        create_data(self)
        self.task.complete = 5
        self.task.save()
        partial_debit(self.project)
        partial_credit([(self.project, Decimal(400), Decimal(0))], Decimal(400))
        ProjectContact.objects.create(
            project=self.project,
            contact=Contact.objects.create(first_name="Ludwig", last_name="von Mises"),
            association=ProjectContact.CUSTOMER,
            is_billable=True
        )
        self.client = Client()
        self.client.login(username='lex@damoti.com', password='pass')


class ProposalViewTests(DocumentTestCase):

    def test_serialize_n_render_proposal(self):

        # serialize

        response = self.client.post(reverse('proposal.create', args=[self.project.id]), {
            'document_date': '2015-07-28',
            'header': 'hello',
            'footer': 'bye',
            'add_terms': True,
            'jobs': self.project.jobs.values_list('id', flat=True)
        })
        self.assertEqual(302, response.status_code)

        # render

        response = self.client.get(reverse('proposal.pdf', args=[
            self.project.id,
            'print',
            Proposal.objects.first().id
        ]), {'with_lineitems': True})
        self.assertEqual(200, response.status_code)

        response = self.client.get(reverse('proposal.pdf', args=[
            self.project.id,
            'email',
            Proposal.objects.first().id
        ]), {'with_lineitems': True})
        self.assertEqual(200, response.status_code)

        response = self.client.get(reverse('specification.pdf', args=[
            self.project.id,
            'email',
            Proposal.objects.first().id
        ]))
        self.assertEqual(200, response.status_code)

    def test_update_proposal(self):

        proposal = Proposal.objects.create(
            project=self.project,
            document_date=timezone.now(),
            json={'header': 'header', 'footer': 'footer'},
            notes='notes',
            amount=1000
        )
        response = self.client.post(reverse('proposal.update', args=[self.project.id, proposal.id]), {
            'document_date': '2015-07-28',
            'header': 'new header',
            'footer': 'new footer',
            'notes': 'new notes'
        })
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse('project.view', args=[self.project.id]))

        proposal.refresh_from_db()
        self.assertEqual(proposal.document_date, date(2015, 7, 28))
        self.assertEqual(proposal.json['header'], 'new header')
        self.assertEqual(proposal.json['footer'], 'new footer')
        self.assertEqual(proposal.notes, 'new notes')


class InvoiceViewTests(DocumentTestCase):

    def test_serialize_n_render_invoice(self):

        # serialize

        response = self.client.post(reverse('invoice.create', args=[self.project.id]), {
            'document_date': '2015-07-28',
            'invoice_no': '1',
            'add_terms': True,
            'title': 'Invoice',
            'header': 'hello',
            'footer': 'bye'
        })
        self.assertEqual(302, response.status_code)

        # render

        response = self.client.get(reverse('invoice.pdf', args=[
            self.project.id,
            'print',
            Invoice.objects.first().id
        ]))
        self.assertEqual(200, response.status_code)

        response = self.client.get(reverse('invoice.pdf', args=[
            self.project.id,
            'email',
            Invoice.objects.first().id
        ]))
        self.assertEqual(200, response.status_code)        

    def test_update_invoice(self):

        invoice = Invoice.objects.create(
            project=self.project,
            document_date=timezone.now(),
            json={'header': 'header', 'footer': 'footer'},
            notes='notes',
            amount=1000
        )
        response = self.client.post(reverse('invoice.update', args=[self.project.id, invoice.id]), {
            'document_date': '2015-07-28',
            'header': 'new header',
            'footer': 'new footer',
            'notes': 'new notes'
        })
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse('project.view', args=[self.project.id]))

        invoice.refresh_from_db()
        self.assertEqual(invoice.document_date, date(2015, 7, 28))
        self.assertEqual(invoice.json['header'], 'new header')
        self.assertEqual(invoice.json['footer'], 'new footer')
        self.assertEqual(invoice.notes, 'new notes')


class EvidenceViewTests(DocumentTestCase):

    def test_generate_evidence(self):
        response = self.client.get(reverse('evidence.pdf', args=[
            self.project.id
        ]))
        self.assertEqual(200, response.status_code)
