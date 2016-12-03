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
        self.project = ProjectFactory()
        self.qs = Project.objects.filter(pk=self.project.id)

    def test_missing_annotations(self):
        project = self.qs.first()  # type: Project
        with self.assertRaises(ValueError):
            self.assertEqual(0, project.estimate)
        with self.assertRaises(ValueError):
            self.assertEqual(0, project.progress)
        with self.assertRaises(ValueError):
            self.assertEqual(0, project.progress_percent)
        with self.assertRaises(ValueError):
            self.assertEqual(False, project.is_billable)

    def test_initial(self):
        project = self.qs.with_totals().first()  # type: Project
        self.assertEqual(0, project.estimate)
        self.assertEqual(0, project.progress)
        self.assertEqual(0, project.progress_percent)
        project = self.qs.with_is_billable().first()  # type: Project
        self.assertEqual(False, project.is_billable)

    def test_correct_annotations(self):
        job = JobFactory(project=self.project)
        TaskFactory(group=job, price=5, complete=10, total=100)
        TaskFactory(group=job, price=5, complete=10, total=100)
        TaskFactory(group=job, price=5, complete=10, total=100, is_provisional=True)
        project = self.qs.with_totals().with_is_billable().first()  # type: Project
        self.assertEqual(200, project.estimate)  # 100 + 100
        self.assertEqual(150, project.progress)  # 50 + 50 + 50
        self.assertEqual(75, project.progress_percent)
        self.assertEqual(True, project.is_billable)


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

