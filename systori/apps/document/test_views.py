from datetime import timedelta, date
from decimal import Decimal
from unittest import skip

from django.test import TestCase, Client
from django.utils import timezone
from django.core.urlresolvers import reverse

from ..accounting.models import Entry
from ..accounting.forms import InvoiceForm
from ..accounting.test_workflow import create_data, A
from ..accounting.workflow import credit_jobs, debit_jobs
from ..directory.models import Contact, ProjectContact
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

    def test_update_proposal(self):

        proposal = Proposal.objects.create(
            project=self.project,
            letterhead=self.letterhead,
            document_date=timezone.now(),
            json={'header': 'header', 'footer': 'footer', 'total_gross': '0'},
            notes='notes'
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

    def setUp(self):
        super().setUp()
        #debit_jobs([(self.job, A(480), Entry.WORK_DEBIT)])
        #credit_jobs([(self.job, A(400), A(), A())], Decimal(400))
        self.task.complete = 5
        self.task.save()

        self.management_form = {}
        _management_form = InvoiceForm(instance=Invoice(project=self.project, json={'debits': []}),
                                       jobs=self.project.jobs.all()).management_form.initial
        for key, value in _management_form.items():
            self.management_form['job-'+key] = value

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
            'job-0-amount_net': '1',
            'job-0-amount_gross': '1',

            'job-1-is_invoiced': 'True',
            'job-1-job': self.job2.id,
            'job-1-amount_net': '1',
            'job-1-amount_gross': '1',
        }
        data.update(self.management_form)
        response = self.client.post(reverse('invoice.create', args=[self.project.id]), data)
        self.assertEqual(302, response.status_code)

        # render

        response = self.client.get(reverse('invoice.pdf', args=[
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
            'job-0-amount_net': '1',
            'job-0-amount_gross': '1',

            'job-1-is_invoiced': 'True',
            'job-1-job': self.job2.id,
            'job-1-amount_net': '1',
            'job-1-amount_gross': '1',
        }
        data.update(self.management_form)
        self.client.post(reverse('invoice.create', args=[self.project.id]), data)


        data = {
            'title': 'Invoice #1',
            'header': 'new header',
            'footer': 'new footer',
            'invoice_no': '2015/01/01',
            'document_date': '2015-07-28',

            'job-0-is_invoiced': 'True',
            'job-0-job': self.job.id,
            'job-0-amount_net': '5',
            'job-0-amount_gross': '5',

            'job-1-is_invoiced': 'True',
            'job-1-job': self.job2.id,
            'job-1-amount_net': '5',
            'job-1-amount_gross': '5',
        }
        data.update(self.management_form)
        invoice = Invoice.objects.order_by('id').first()
        response = self.client.post(reverse('invoice.update', args=[self.project.id, invoice.id]), data)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse('project.view', args=[self.project.id]))

        invoice.refresh_from_db()
        self.assertEqual(invoice.document_date, date(2015, 7, 28))
        self.assertEqual(invoice.json['header'], 'new header')
        self.assertEqual(invoice.json['footer'], 'new footer')


class EvidenceViewTests(DocumentTestCase):

    def test_generate_evidence(self):
        response = self.client.get(reverse('evidence.pdf', args=[
            self.project.id
        ]))
        self.assertEqual(200, response.status_code)


class LetterheadCreateTests(DocumentTestCase):

    def test_post(self):
        letterhead_count = Letterhead.objects.count()
        with open('systori/apps/document/test_data/letterhead.pdf', 'rb') as lettehead_pdf:
            response = self.client.post(
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
        self.assertRedirects(response, reverse('letterhead.update', args=[Letterhead.objects.latest('pk').pk]))
