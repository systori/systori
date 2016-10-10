import os
from unittest import skip
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.translation import activate
from ..document.models import *
from .models import *

from ..company.factories import *
from ..project.factories import *
from ..task.factories import *
from ..user.factories import *

User = get_user_model()


def create_task_data(self, create_user=True, create_company=True):
    if create_company:
        self.company = CompanyFactory()
    if create_user:
        self.user = UserFactory(company=self.company)
    letterhead_pdf = os.path.join(settings.BASE_DIR, 'apps/document/test_data/letterhead.pdf')
    self.letterhead = Letterhead.objects.create(name="Test Letterhead", letterhead_pdf=letterhead_pdf)
    DocumentSettings.objects.create(language='de',
                                    evidence_letterhead=self.letterhead,
                                    proposal_letterhead=self.letterhead,
                                    invoice_letterhead=self.letterhead)
    self.project = ProjectFactory()
    self.project2 = ProjectFactory(has_level_3=True)
    self.job = JobFactory(project=self.project)
    self.job2 = JobFactory(project=self.project)
    self.group = GroupFactory(name="my group", job=self.job, level=2)
    self.group2 = GroupFactory(name="my group 2", job=self.job, level=2)
    self.group2.generate_children()
    self.task = TaskFactory(name="my task one", qty=10, taskgroup=self.group, job=self.job, status=Task.RUNNING)
    TaskInstanceFactory(task=self.task, selected=True, unit_price=96)
    self.lineitem = LineItemFactory(unit_qty=8, price=12, taskinstance=self.task.instance)
    self.task2 = TaskFactory(name="my task two", qty=0, taskgroup=self.group, job=self.job)
    TaskInstanceFactory(task=self.task2, selected=True, unit_price=0)
    self.lineitem2 = LineItemFactory(unit_qty=0, price=0, taskinstance=self.task2.instance)
    self.group3 = GroupFactory(job=self.job2, level=2)
    self.task3 = TaskFactory(name="my task one", qty=10, taskgroup=self.group3, job=self.job2)
    TaskInstanceFactory(task=self.task3, selected=True, unit_price=96)
    self.lineitem3 = LineItemFactory(unit_qty=8, price=12, taskinstance=self.task3.instance)


class TaskCalculationTests(TestCase):

    def setUp(self):
        CompanyFactory()
        self.job = JobFactory(project=ProjectFactory())

    def test_task_zero_total(self):
        task = TaskFactory(group=self.job)
        self.assertEqual(0, task.estimate)
        self.assertEqual(0, task.progress)

    def test_task_estimate(self):
        task = TaskFactory(group=self.job, qty=2, unit_price=7)
        self.assertEqual(14, task.estimate)

    def test_provisional_task_estimate(self):
        """ Provisional tasks are not included in the estimate total. """
        task = TaskFactory(group=self.job, qty=2, unit_price=7)
        self.assertEqual(14, task.estimate)
        task.is_provisional = True
        self.assertEqual(0, task.estimate)

    def test_variant_task_estimate(self):
        """ Only the variant with serial 0 (default variant) is included in estimates. """
        task = TaskFactory(group=self.job, qty=2, unit_price=7, variant_group=1)
        self.assertEqual(14, task.estimate)
        task.variant_serial = 1
        self.assertEqual(0, task.estimate)

    def test_task_progress_with_value(self):
        """ Progress from completion is always counted regardless of is_provisional or variant serial."""
        task = TaskFactory(group=self.job, complete=2, unit_price=7)
        self.assertEqual(14, task.progress)
        task.is_provisional = True
        self.assertEqual(14, task.progress)
        task.variant_group = 1
        task.variant_serial = 1
        self.assertEqual(14, task.progress)


class GroupCalculationTests(TestCase):

    def setUp(self):
        CompanyFactory()
        self.job = JobFactory(project=ProjectFactory())

    def test_empty_group_is_zero(self):
        group = GroupFactory(parent=self.job)
        self.assertEqual(0, group.estimate)

    def test_group_with_tasks(self):
        group = GroupFactory(parent=self.job)
        TaskFactory(group=group, qty=2, unit_price=7)
        TaskFactory(group=group, qty=2, unit_price=8)
        self.assertEqual(30, group.estimate)

    def test_multiple_subgroups(self):
        group = GroupFactory(parent=self.job)
        subgroup1 = GroupFactory(parent=group)
        TaskFactory(group=subgroup1, qty=2, unit_price=7)
        subgroup2 = GroupFactory(parent=group)
        TaskFactory(group=subgroup2, qty=2, unit_price=8)
        self.assertEqual(14, subgroup1.estimate)
        self.assertEqual(16, subgroup2.estimate)
        self.assertEqual(30, group.estimate)
        self.assertEqual(30, self.job.estimate)


class JobQuerySetTests(TestCase):

    def setUp(self):
        create_task_data(self)
        self.job2 = Job.objects.create(job_code=3, name="Empty Job", project=self.project)

    def test_zero_total(self):
        jobs = Job.objects.filter(pk=self.job2.id)
        self.assertEqual(0, jobs.estimate_total())
        self.assertEqual(0, jobs.progress_total())

    def test_nonzero_total(self):
        jobs = Job.objects
        self.assertEqual(Decimal(1920), jobs.estimate_total())
        self.assertEqual(Decimal(0), jobs.progress_total())


class JobEstimateModificationTests(TestCase):
    def setUp(self):
        create_task_data(self)

    @skip
    def test_increase_total(self):
        self.assertEqual(Decimal(960), self.job.estimate_total)
        self.job.estimate_total_modify(self.user, 'increase')
        self.assertEqual(Decimal(960 * (Job.ESTIMATE_INCREMENT + 1)), self.job.estimate_total)

    @skip
    def test_2x_increase_total(self):
        self.assertEqual(Decimal(960), self.job.estimate_total)
        self.job.estimate_total_modify(self.user, 'increase')
        self.job.estimate_total_modify(self.user, 'increase')
        first = Decimal(960) * Decimal(Job.ESTIMATE_INCREMENT)
        second = first + (Decimal(960) + first) * Decimal(Job.ESTIMATE_INCREMENT)
        self.assertEqual(round(Decimal(960) + second, 2), round(self.job.estimate_total, 2))

    @skip
    def test_decrease_total(self):
        self.assertEqual(Decimal(960), self.job.estimate_total)
        self.job.estimate_total_modify(self.user, 'decrease')
        self.assertEqual(Decimal(960 * (1 - Job.ESTIMATE_INCREMENT)), self.job.estimate_total)

    @skip
    def test_2x_decrease_total(self):
        self.assertEqual(Decimal(960), self.job.estimate_total)
        self.job.estimate_total_modify(self.user, 'decrease')
        self.job.estimate_total_modify(self.user, 'decrease')
        first = Decimal(960) * Decimal(Job.ESTIMATE_INCREMENT) * -1
        second = first - (Decimal(960) + first) * Decimal(Job.ESTIMATE_INCREMENT)
        self.assertEqual(round(Decimal(960) + second, 2), round(self.job.estimate_total, 2))

    @skip
    def test_decrease_increase_total(self):
        self.assertEqual(Decimal(960), self.job.estimate_total)
        self.job.estimate_total_modify(self.user, 'decrease')
        self.job.estimate_total_modify(self.user, 'increase')
        first = Decimal(960) * Decimal(Job.ESTIMATE_INCREMENT) * -1
        second = first + (Decimal(960) + first) * Decimal(Job.ESTIMATE_INCREMENT)
        self.assertEqual(round(Decimal(960) + second, 2), round(self.job.estimate_total, 2))

    def test_reset_total(self):
        self.job.estimate_total_modify(self.user, 'increase')
        self.job.estimate_total_modify(self.user, 'reset')
        self.assertEqual(Decimal(960), self.job.estimate_total)


class TestJobTransitions(TestCase):
    def setUp(self):
        activate('en')
        create_task_data(self)

    def test_job_draft(self):
        self.assertEquals('Draft', self.job.get_status_display())

    def test_job_proposed(self):
        proposal = Proposal.objects.create(project=self.project, letterhead=self.letterhead)
        proposal.jobs.add(self.job)
        self.job.refresh_from_db()
        self.assertEquals('Proposed', self.job.get_status_display())

    def test_job_approved(self):
        proposal = Proposal.objects.create(project=self.project, letterhead=self.letterhead)
        proposal.jobs.add(self.job)
        proposal.send()
        proposal.approve()
        self.job.refresh_from_db()
        self.assertEquals('Approved', self.job.get_status_display())

    def test_job_declined(self):
        proposal = Proposal.objects.create(project=self.project, letterhead=self.letterhead)
        proposal.jobs.add(self.job)
        self.job.refresh_from_db()
        self.assertEquals('Proposed', self.job.get_status_display())
        proposal.send()
        proposal.decline()
        self.job.refresh_from_db()
        self.assertEquals('Draft', self.job.get_status_display())

    def test_job_after_proposal_deleted(self):
        proposal = Proposal.objects.create(project=self.project, letterhead=self.letterhead)
        proposal.jobs.add(self.job)
        self.job.refresh_from_db()
        self.assertEquals('Proposed', self.job.get_status_display())
        proposal.delete()
        self.job.refresh_from_db()
        self.assertEquals('Draft', self.job.get_status_display())


class TaskTest(TestCase):

    def test_complete_percent(self):
        task = Task(complete=10, qty=0)
        self.assertEqual(task.complete_percent, 0)
        task.qty = 10
        self.assertEqual(task.complete_percent, 100)
