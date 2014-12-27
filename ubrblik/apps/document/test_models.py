from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import *

from ..task.test_models import create_task_data


class ProposalTests(TestCase):

    def setUp(self):
        create_task_data(self)

    def test_proposal_new(self):
        d = Proposal.objects.create(project=self.project, amount=Decimal(0.0))
        self.assertEquals('New', d.get_status_display())
        self.assertEquals(['Send'], [t.custom['label'] for t in d.get_available_status_transitions()])

    def test_proposal_send(self):
        d = Proposal.objects.create(project=self.project, amount=Decimal(0.0))
        d.send(); d.save()
        d = Proposal.objects.get(pk=d.pk)
        self.assertEquals('Sent', d.get_status_display())
        self.assertEquals(['Approve', 'Decline'], [t.custom['label'] for t in d.get_available_status_transitions()])