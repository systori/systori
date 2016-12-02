from django.test import TestCase
from django.utils.translation import activate

from ..company.factories import CompanyFactory
from ..task.factories import JobFactory, TaskFactory
from ..document.factories import ProposalFactory, LetterheadFactory

from .factories import ProjectFactory
from .models import Project


class ProjectTotalTests(TestCase):

    def setUp(self):
        CompanyFactory()

    def test_zero(self):
        project = ProjectFactory()  # type: Project
        self.assertEqual(0, project.estimate)

    def test_nonzero(self):
        project = ProjectFactory()  # type: Project
        job = JobFactory(project=project)
        TaskFactory(group=job, total=1920)
        self.assertEqual(1920, project.estimate)


class ProjectPhaseTests(TestCase):

    def setUp(self):
        activate('en')
        CompanyFactory()
        self.project = ProjectFactory()
        self.letterhead = LetterheadFactory()

    def test_project_new(self):
        self.assertEquals('Prospective', self.project.get_phase_display())
        self.assertEquals('Active', self.project.get_state_display())

    def test_project_with_proposal(self):
        ProposalFactory(project=self.project, letterhead=self.letterhead)
        self.project.refresh_from_db()
        self.assertEquals('Tendering', self.project.get_phase_display())
        self.assertEquals('Active', self.project.get_state_display())

    def test_project_with_approved_proposal(self):
        proposal = ProposalFactory(project=self.project, letterhead=self.letterhead)
        proposal.send()
        proposal.save()
        proposal.approve()
        proposal.save()
        self.project.refresh_from_db()
        self.assertEquals('Planning', self.project.get_phase_display())
        self.assertEquals('Active', self.project.get_state_display())

    def test_project_with_started_job(self):
        # first get to planning
        proposal = ProposalFactory(project=self.project, letterhead=self.letterhead)
        proposal.send()
        proposal.save()
        proposal.approve()
        proposal.save()

        # now get to executing
        job = JobFactory(project=self.project)
        job.status = job.STARTED
        job.save()

        self.project.refresh_from_db()
        self.assertEquals('Executing', self.project.get_phase_display())
        self.assertEquals('Active', self.project.get_state_display())

