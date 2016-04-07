from datetime import timedelta, date
from decimal import Decimal
from unittest import skip

from django.test import TestCase, Client
from django.test.client import MULTIPART_CONTENT
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.conf import settings

from ..accounting.models import Entry
from ..accounting.forms import InvoiceForm, InvoiceFormSet
from ..accounting.test_workflow import create_data, A
from ..accounting.workflow import credit_jobs, debit_jobs
from ..directory.models import Contact, ProjectContact
from .forms import ProposalForm, ProposalFormSet
from .models import Proposal, Invoice, Letterhead


def template_debug_output():
    """ Usage:

        try:
            self.client.get(...)
        except:
            template_debug_output()
    """
    import sys
    import html
    from django.views.debug import ExceptionReporter
    reporter = ExceptionReporter(None, *sys.exc_info())
    reporter.get_template_exception_info()
    info = reporter.template_info
    print()
    print('Exception Message: '+info['message'])
    print('Template: '+info['name'])
    print()
    for line in info['source_lines']:
        if line[0] == info['line']:
            print('-->'+html.unescape(line[1])[3:-1])
        else:
            print(html.unescape(line[1])[:-1])


class DocumentTestCase(TestCase):

    def setUp(self):
        create_data(self)
        ProjectContact.objects.create(
            project=self.project,
            contact=Contact.objects.create(first_name="Ludwig", last_name="von Mises"),
            association=ProjectContact.CUSTOMER,
            is_billable=True
        )
        self.client = Client()
        self.client.login(username=self.user.email, password='open sesame')

    def client_get(self, path, data=None, follow=False, secure=False, **extra):
        extra['HTTP_HOST'] = self.company.schema + '.' + settings.SERVER_NAME
        return self.client.get(path, data, follow, secure, **extra)

    def client_post(self, path, data=None, content_type=MULTIPART_CONTENT,
             follow=False, secure=False, **extra):
        extra['HTTP_HOST'] = self.company.schema + '.' + settings.SERVER_NAME
        return self.client.post(path, data, content_type, follow, secure, **extra)

    def make_management_form(self):
        data = {}
        instance = self.model(project=self.project, json={'jobs': []})
        jobs = self.project.jobs.all()
        _form_set = self.form_set(instance=instance, jobs=jobs)
        for key, value in _form_set.management_form.initial.items():
            data['job-'+key] = value
        return data


class ProposalViewTests(DocumentTestCase):
    model = Proposal
    form = ProposalForm
    form_set = ProposalFormSet

    def test_serialize_n_render_proposal(self):

        # serialize
        data = {
            'title': 'Proposal #1',
            'document_date': '2015-01-01',
            'header': 'hello',
            'footer': 'bye',
            'add_terms': True,
            'job-0-job': self.job.id,
            'job-0-is_attached': 'True',
            'job-1-job': self.job2.id,
            'job-1-is_attached': 'True',
        }
        data.update(self.make_management_form())

        response = self.client_post(reverse('proposal.create', args=[self.project.id]), data)
        self.assertEqual(302, response.status_code)

        # render

        response = self.client_get(reverse('proposal.pdf', args=[
            self.project.id,
            'print',
            Proposal.objects.first().id
        ]), {'with_lineitems': True})
        self.assertEqual(200, response.status_code)

        response = self.client_get(reverse('proposal.pdf', args=[
            self.project.id,
            'email',
            Proposal.objects.first().id
        ]), {'with_lineitems': True})
        self.assertEqual(200, response.status_code)

    def test_update_proposal(self):

        proposal = Proposal.objects.create(
            project=self.project,
            letterhead=self.letterhead,
            document_date=timezone.now(),
            json={'header': 'header', 'footer': 'footer', 'total_gross': '0', 'jobs': []},
            notes='notes'
        )
        data = {
            'title': 'Proposal #1',
            'document_date': '2015-07-28',
            'header': 'new header',
            'footer': 'new footer',
            'notes': 'new notes',
            'add_terms': True,
            'job-0-job': self.job.id,
            'job-0-is_attached': 'True',
            'job-1-job': self.job2.id,
            'job-1-is_attached': 'True',
        }
        data.update(self.make_management_form())
        response = self.client_post(reverse('proposal.update', args=[self.project.id, proposal.id]), data)
        self.assertEqual(302, response.status_code)
        #self.assertRedirects(response, reverse('project.view', args=[self.project.id]))

        proposal.refresh_from_db()
        self.assertEqual(proposal.document_date, date(2015, 7, 28))
        self.assertEqual(proposal.json['header'], 'new header')
        self.assertEqual(proposal.json['footer'], 'new footer')
        self.assertEqual(proposal.notes, 'new notes')


class InvoiceViewTests(DocumentTestCase):
    model = Invoice
    form = InvoiceForm
    form_set = InvoiceFormSet

    def setUp(self):
        super().setUp()
        self.task.complete = 5
        self.task.save()

    def test_serialize_n_render_invoice(self):

        # serialize

        data = {
            'title': 'Invoice #1',
            'header': 'The Header',
            'footer': 'The Footer',
            'invoice_no': '2015/01/01',
            'document_date': '2015-01-01',

            'job-0-is_invoiced': 'True',
            'job-0-job': self.job.id,
            'job-0-debit_net': '1',
            'job-0-debit_tax': '1',

            'job-1-is_invoiced': 'True',
            'job-1-job': self.job2.id,
            'job-1-debit_net': '1',
            'job-1-debit_tax': '1',
        }
        data.update(self.make_management_form())
        response = self.client_post(reverse('invoice.create', args=[self.project.id]), data)
        self.assertEqual(302, response.status_code)

        # render

        response = self.client_get(reverse('invoice.pdf', args=[
            self.project.id,
            'print',
            Invoice.objects.first().id
        ]))
        self.assertEqual(200, response.status_code)

    def test_update_invoice(self):

        data = {
            'title': 'Invoice #1',
            'header': 'The Header',
            'footer': 'The Footer',
            'invoice_no': '2015/01/01',
            'document_date': '2015-01-01',

            'job-0-is_invoiced': 'True',
            'job-0-job': self.job.id,
            'job-0-debit_net': '1',
            'job-0-debit_tax': '1',

            'job-1-is_invoiced': 'True',
            'job-1-job': self.job2.id,
            'job-1-debit_net': '1',
            'job-1-debit_tax': '1',
        }
        data.update(self.make_management_form())
        self.client_post(reverse('invoice.create', args=[self.project.id]), data)


        data = {
            'title': 'Invoice #1',
            'header': 'new header',
            'footer': 'new footer',
            'invoice_no': '2015/01/01',
            'document_date': '2015-07-28',

            'job-0-is_invoiced': 'True',
            'job-0-job': self.job.id,
            'job-0-debit_net': '5',
            'job-0-debit_tax': '5',

            'job-1-is_invoiced': 'True',
            'job-1-job': self.job2.id,
            'job-1-debit_net': '5',
            'job-1-debit_tax': '5',
        }
        data.update(self.make_management_form())
        invoice = Invoice.objects.order_by('id').first()
        response = self.client_post(reverse('invoice.update', args=[self.project.id, invoice.id]), data)
        self.assertEqual(302, response.status_code)
        #self.assertRedirects(response, reverse('project.view', args=[self.project.id]))

        invoice.refresh_from_db()
        self.assertEqual(invoice.document_date, date(2015, 7, 28))
        self.assertEqual(invoice.json['header'], 'new header')
        self.assertEqual(invoice.json['footer'], 'new footer')


class EvidenceViewTests(DocumentTestCase):

    def test_generate_evidence(self):
        response = self.client_get(reverse('evidence.pdf', args=[
            self.project.id
        ]))
        self.assertEqual(200, response.status_code)


class LetterheadCreateTests(DocumentTestCase):

    def test_post(self):
        letterhead_count = Letterhead.objects.count()
        with open('systori/apps/document/test_data/letterhead.pdf', 'rb') as lettehead_pdf:
            response = self.client_post(
                reverse('letterhead.create'),
                {
                    'document_unit': Letterhead.mm,
                    'top_margin': 10,
                    'right_margin': 10,
                    'bottom_margin': 10,
                    'left_margin': 10,
                    'letterhead_pdf': lettehead_pdf,
                    'document_format': Letterhead.A4,
                    'orientation': Letterhead.PORTRAIT
                }
            )
        self.assertEqual(Letterhead.objects.count(), letterhead_count + 1)
        #self.assertRedirects(response, reverse('letterhead.update', args=[Letterhead.objects.latest('pk').pk]))
