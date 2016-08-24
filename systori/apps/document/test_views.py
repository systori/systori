from datetime import date

from django.utils import timezone
from django.core.urlresolvers import reverse

from systori.lib.testing import SystoriTestCase
from ..accounting.test_workflow import create_data
from ..accounting.test_views import DocumentTestCase
from ..company.models import Access
from .forms import ProposalForm, ProposalFormSet
from .models import Proposal, Letterhead


class ProposalViewTests(DocumentTestCase):
    model = Proposal
    form = ProposalForm
    form_set = ProposalFormSet

    def test_serialize_n_render_proposal(self):

        response = self.client.get(reverse('proposal.create', args=[self.project.id]))
        self.assertEqual(200, response.status_code)

        data = self.form_data({
            'title': 'Proposal #1',
            'document_date': '2015-01-01',
            'header': 'hello',
            'footer': 'bye',
            'add_terms': True,
            'job-0-job_id': self.job.id,
            'job-0-is_attached': 'True',
            'job-1-job_id': self.job2.id,
            'job-1-is_attached': 'True',
        })
        response = self.client.post(reverse('proposal.create', args=[self.project.id]), data)
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
            json={'header': 'header', 'footer': 'footer', 'total_gross': '0', 'jobs': []},
            notes='notes'
        )
        data = self.form_data({
            'title': 'Proposal #1',
            'document_date': '2015-07-28',
            'header': 'new header',
            'footer': 'new footer',
            'notes': 'new notes',
            'add_terms': True,
            'job-0-job_id': self.job.id,
            'job-0-is_attached': 'True',
            'job-1-job_id': self.job2.id,
            'job-1-is_attached': 'True',
        })
        response = self.client.post(reverse('proposal.update', args=[self.project.id, proposal.id]), data)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse('project.view', args=[self.project.id]))

        proposal.refresh_from_db()
        self.assertEqual(proposal.document_date, date(2015, 7, 28))
        self.assertEqual(proposal.json['header'], 'new header')
        self.assertEqual(proposal.json['footer'], 'new footer')
        self.assertEqual(proposal.notes, 'new notes')


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


class InvoiceListViewTest(SystoriTestCase):

    def setUp(self):
        create_data(self)
        access = Access.objects.get(user=self.user)
        access.is_owner = True
        access.save()
        self.client.login(username=self.user.email, password='open sesame')

    def test_kwarg_queryset_filter(self):
        response = self.client.get(reverse('invoice.list'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('invoice.list', kwargs={'status_filter': 'sent'}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('invoice.list', kwargs={'status_filter': 'paid'}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('invoice.list', kwargs={'status_filter': 'draft'}))
        self.assertEqual(response.status_code, 200)
