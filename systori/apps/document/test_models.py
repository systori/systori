from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.translation import activate
from .models import *

from ..task.test_models import create_task_data
from ..directory.test_models import create_contact_data
from ..directory.models import ProjectContact


class ProposalTests(TestCase):
    def setUp(self):
        activate('en')
        create_task_data(self)

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
        create_contact_data(self)
        self.pc = ProjectContact.objects.create(project=self.project, contact=self.contact, is_billable=True)

    def test_render_english_tpl(self):
        d = DocumentTemplate.objects.create(name="DocTpl", header="Dear [lastname]", footer="Thanks [firstname]!",
                                            document_type="invoice")
        activate('en')
        r = d.render(self.project)
        self.assertEqual("Dear von Mises", r['header'])
        self.assertEqual("Thanks Ludwig!", r['footer'])

    def test_render_german_tpl(self):
        d = DocumentTemplate.objects.create(name="DocTpl", header="Dear [Nachname]", footer="Thanks [Vorname]!",
                                            document_type="invoice")
        activate('de')
        r = d.render(self.project)
        self.assertEqual("Dear von Mises", r['header'])
        self.assertEqual("Thanks Ludwig!", r['footer'])

    def test_render_sample_tpl(self):
        d = DocumentTemplate.objects.create(name="DocTpl", header="Dear [lastname]", footer="Thanks [firstname]!",
                                            document_type="invoice")
        activate('en')
        r = d.render()
        self.assertEqual("Dear Smith", r['header'])
        self.assertEqual("Thanks John!", r['footer'])
