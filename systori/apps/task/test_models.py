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
        self.user = UserFactory(company=self.company, password='open sesame')
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
    self.group = TaskGroupFactory(name="my group", job=self.job, level=2)
    self.group2 = TaskGroupFactory(name="my group 2", job=self.job, level=2)
    self.group2.generate_children()
    self.task = TaskFactory(name="my task one", qty=10, taskgroup=self.group, job=self.job, status=Task.RUNNING)
    TaskInstanceFactory(task=self.task, selected=True, unit_price=96)
    self.lineitem = LineItemFactory(unit_qty=8, price=12, taskinstance=self.task.instance)
    self.task2 = TaskFactory(name="my task two", qty=0, taskgroup=self.group, job=self.job)
    TaskInstanceFactory(task=self.task2, selected=True, unit_price=0)
    self.lineitem2 = LineItemFactory(unit_qty=0, price=0, taskinstance=self.task2.instance)
    self.group3 = TaskGroupFactory(job=self.job2, level=2)
    self.task3 = TaskFactory(name="my task one", qty=10, taskgroup=self.group3, job=self.job2)
    TaskInstanceFactory(task=self.task3, selected=True, unit_price=96)
    self.lineitem3 = LineItemFactory(unit_qty=8, price=12, taskinstance=self.task3.instance)


class TaskTotalTests(TestCase):

    def setUp(self):
        create_task_data(self)

    def test_zero_total(self):
        task = Task.objects.get(pk=self.task2.pk)
        self.assertEqual(0, task.fixed_price_estimate)
        self.assertEqual(0, task.fixed_price_progress)

    def test_non_zero_total(self):
        self.task.instance.unit_price = 80
        self.assertEqual(800, self.task.fixed_price_estimate)


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


class TaskGroupOffsetTests(TestCase):
    def setUp(self):
        CompanyFactory.create()
        project = ProjectFactory.create()
        self.job = JobFactory.create(job_code=1, project=project)
        self.group = TaskGroupFactory.create(job=self.job, level=2)

    def test_no_offset(self):
        self.assertEqual('1.1', self.group.code)

    def test_offset_4(self):
        self.job.taskgroup_offset = 3
        self.assertEqual('1.4', self.group.code)


class CodeTests(TestCase):
    def test_default_code(self):
        CompanyFactory()
        project = ProjectFactory()
        job = JobFactory(job_code=1, project=project)
        group = TaskGroupFactory(job=job, level=2)
        task = TaskFactory(taskgroup=group)
        self.assertEqual('1', job.code)
        self.assertEqual('1.1', group.code)
        self.assertEqual('1.1.1', task.code)

        TaskInstanceFactory(task=task, selected=True)
        self.assertEqual('1.1.1', task.instance.code)
        TaskInstanceFactory(task=task)
        self.assertEqual('1.1.1a', task.instance.code)
        self.assertEqual('1.1.1b', task.taskinstances.all()[1].code)


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


class TaskCloneTests(TestCase):
    def setUp(self):
        create_task_data(self)

    def test_clone(self):
        new_job = Job.objects.create(job_code=5, name="New", project=self.project)
        self.assertEqual(len(new_job.taskgroups), 0)
        self.job.clone_to(new_job)

        job = Job.objects.get(pk=new_job.pk)
        self.assertEqual(len(job.taskgroups), 2)
        group = job._taskgroups.get(name="my group")
        self.assertNotEqual(group.id, self.group.id)
        self.assertEqual(group.tasks.count(), 2)
        self.assertFalse(max(group.tasks.values_list('status', flat=True)))


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


class TaskGroupTest(TestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.user = UserFactory(company=self.company, password='open sesame')
        self.project = ProjectFactory(has_level_3=True, has_level_4=True)
        self.job = JobFactory(project=self.project)
        self.group = TaskGroupFactory(name="my group", job=self.job, level=2)

    def test_generate_children(self):

        self.assertEquals(0, self.group.children.count())

        self.group.generate_children()

        self.assertEquals(1, len(self.job.taskgroups))  # Level 2
        self.assertEquals(1, self.group.children.count())  # Level 3
        self.assertEquals(1, self.group.children.first().children.count())  # Level 4
        self.assertEquals(0, self.group.children.first().children.first().children.count())  # Level 5

    def test_prefetching(self):

        def add_lineitems_n_stuff(group):
            task = TaskFactory(taskgroup=group)
            inst = TaskInstanceFactory(task=task, selected=True)
            li = LineItemFactory(taskinstance=inst)

        self.group.generate_children()
        add_lineitems_n_stuff(self.group.children.first().children.first())

        self.group2 = TaskGroupFactory(name='second', parent=self.group, job=self.job, level=3)
        self.group2.generate_children()
        add_lineitems_n_stuff(self.group2.children.first())

        self.group3 = TaskGroupFactory(name='second', parent=self.group2, job=self.job, level=4)
        self.group3.generate_children()  # nothing should happen, we're at level 4
        add_lineitems_n_stuff(self.group3)

        self.assertEquals(1, self.job._taskgroups.filter(level=2).count())

        def traverse_children(groups):
            groups[0].children.all()[0].children.all()[0].tasks.first().instance.lineitems.first()
            groups[0].children.all()[1].children.all()[0].tasks.first().instance.lineitems.first()
            groups[0].children.all()[1].children.all()[1].tasks.first().instance.lineitems.first()

        # no prefetch
        with self.assertNumQueries(18):
            traverse_children(self.job._taskgroups.filter(level=2).all())

        # with prefetch
        with self.assertNumQueries(6):
            traverse_children(self.job.taskgroups)
