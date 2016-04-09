from datetime import date

from django.utils import timezone
from django.core.urlresolvers import reverse

from systori.lib.testing import SystoriTestCase
from ..accounting.test_workflow import create_data
from ..directory.models import Contact, ProjectContact
from .forms import ProposalForm, ProposalFormSet
from .models import Proposal, Letterhead


class DocumentTestCase(SystoriTestCase):

    def setUp(self):
        super().setUp()
        create_data(self)
        ProjectContact.objects.create(
            project=self.project,
            contact=Contact.objects.create(first_name="Ludwig", last_name="von Mises"),
            association=ProjectContact.CUSTOMER,
            is_billable=True
        )
        self.client.login(username=self.user.email, password='open sesame')

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
        response = self.client.post(reverse('proposal.update', args=[self.project.id, proposal.id]), data)
        self.assertEqual(302, response.status_code)
        #self.assertRedirects(response, reverse('project.view', args=[self.project.id]))

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
        #self.assertRedirects(response, reverse('letterhead.update', args=[Letterhead.objects.latest('pk').pk]))
