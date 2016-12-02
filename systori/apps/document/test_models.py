from django.test import TestCase
from django.utils.translation import activate

from ..company.factories import CompanyFactory
from ..project.factories import ProjectFactory
from ..directory.factories import ContactFactory

from .models import Proposal
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

    def test_proposal_new(self):
        d = Proposal.objects.create(project=self.project, letterhead=self.letterhead)
        self.assertEquals('New', d.get_status_display())
        self.assertEquals(['Send'], [t.custom['label'] for t in d.get_available_status_transitions()])

    def test_proposal_send(self):
        d = Proposal.objects.create(project=self.project, letterhead=self.letterhead)
        d.send();
        d.save()
        d = Proposal.objects.get(pk=d.pk)
        self.assertEquals('Sent', d.get_status_display())
        # TODO: for some reason result of get_available_status_transitions() is not consistently sorted
        labels = [str(t.custom['label']) for t in d.get_available_status_transitions()]
        labels.sort()
        self.assertEquals(['Approve', 'Decline'], labels)


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
