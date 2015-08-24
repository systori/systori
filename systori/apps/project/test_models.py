from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.translation import activate
from ..task.models import *
from ..document.models import *
from .models import *

from ..task.test_models import create_task_data

User = get_user_model()


class ProjectTotalTests(TestCase):
    def setUp(self):
        create_task_data(self)

    def test_zero(self):
        project = Project.objects.get(pk=self.project2.pk)
        self.assertEqual(0, project.estimate_total)

    def test_nonzero(self):
        project = Project.objects.get(pk=self.project.pk)
        self.assertEqual(1920, project.estimate_total)


class ProjectPhaseTests(TestCase):
    def setUp(self):
        activate('en')
        create_task_data(self)

    def test_project_new(self):
        self.assertEquals('Prospective', self.project.get_phase_display())
        self.assertEquals('Active', self.project.get_state_display())

    def test_project_with_proposal(self):
        Proposal.objects.create(amount=99, project=self.project)
        self.project.refresh_from_db()
        self.assertEquals('Tendering', self.project.get_phase_display())
        self.assertEquals('Active', self.project.get_state_display())

    def test_project_with_approved_proposal(self):
        proposal = Proposal.objects.create(amount=99, project=self.project)
        proposal.send();
        proposal.save()
        proposal.approve();
        proposal.save()
        self.project.refresh_from_db()
        self.assertEquals('Planning', self.project.get_phase_display())
        self.assertEquals('Active', self.project.get_state_display())

    def test_project_with_started_job(self):
        # first get to planning
        proposal = Proposal.objects.create(amount=99, project=self.project)
        proposal.send();
        proposal.save()
        proposal.approve();
        proposal.save()

        # now get to executing
        self.job.status = self.job.STARTED
        self.job.save()

        self.project.refresh_from_db()
        self.assertEquals('Executing', self.project.get_phase_display())
        self.assertEquals('Active', self.project.get_state_display())

