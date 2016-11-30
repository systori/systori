import os
import datetime
from unittest import skip
from django.test import TestCase
from django.utils.translation import activate
from django.conf import settings

from .models import Group, Task

from ..company.factories import CompanyFactory
from ..project.factories import ProjectFactory
from ..document.factories import ProposalFactory, LetterheadFactory
from ..task.factories import JobFactory, GroupFactory, TaskFactory
from ..user.factories import UserFactory


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


class CalculationTests(TestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.job = JobFactory(project=ProjectFactory())

    def test_task_zero(self):
        task = TaskFactory(group=self.job)
        self.assertEqual(task.total, 0)
        self.assertEqual(task.progress, 0)

    def test_task_with_progress(self):
        task = TaskFactory(group=self.job, qty=5, complete=3, price=8)
        self.assertTrue(task.is_billable)
        self.assertEqual(task.progress, 24)
        self.assertEqual(task.complete_percent, 60)

    def test_task_estimate_determination(self):
        """ Determines if a task should be included in totals. """
        self.assertEqual(TaskFactory(group=self.job).include_estimate, True)

        # provisional tasks
        self.assertEqual(TaskFactory(group=self.job, is_provisional=True).include_estimate, False)

        # variant tasks
        self.assertEqual(TaskFactory(group=self.job, variant_group=1).include_estimate, True)
        self.assertEqual(TaskFactory(group=self.job, variant_group=1, variant_serial=1).include_estimate, False)

    def test_complete_percent(self):
        # Division by zero
        self.assertEqual(TaskFactory(group=self.job, complete=10, qty=0).complete_percent, 0)
        # Complete greater than qty
        self.assertEqual(TaskFactory(group=self.job, complete=10, qty=5).complete_percent, 200)
        # 100% rounding
        self.assertEqual(TaskFactory(group=self.job, complete=99.99, qty=100).complete_percent, 100)
        self.assertEqual(TaskFactory(group=self.job, complete=100.01, qty=100).complete_percent, 100)

    def test_empty_group_is_zero(self):
        self.assertEqual(0, GroupFactory(parent=self.job).total)

    def test_group_with_tasks(self):
        group = GroupFactory(parent=self.job)
        TaskFactory(group=group, total=7)
        TaskFactory(group=group, total=8)
        self.assertEqual(15, group.total)

    def test_multiple_subgroups(self):
        group = GroupFactory(parent=self.job)
        subgroup1 = GroupFactory(parent=group)
        TaskFactory(group=subgroup1, total=7)
        subgroup2 = GroupFactory(parent=group)
        TaskFactory(group=subgroup2, total=8)
        self.assertEqual(7, subgroup1.total)
        self.assertEqual(8, subgroup2.total)
        self.assertEqual(15, group.total)
        self.assertEqual(15, self.job.total)

    def test_provisional_task_estimate(self):
        """ Provisional tasks are not included in the estimate total. """
        task = TaskFactory(group=self.job, total=14)
        self.assertEqual(14, self.job.total)
        task.is_provisional = True
        task.save()
        self.assertEqual(0, self.job.total)

    def test_variant_task_estimate(self):
        """ Only the variant with serial 0 (default variant) is included in estimates. """
        task = TaskFactory(group=self.job, total=14, variant_group=1)
        self.assertEqual(14, self.job.total)
        task.variant_serial = 1
        task.save()
        self.assertEqual(0, self.job.total)

    def test_task_progress_with_value(self):
        """ Progress from completion is always counted regardless of is_provisional or variant serial."""
        task = TaskFactory(group=self.job, complete=2, price=10)
        self.assertEqual(20, self.job.progress)
        task.is_provisional = True
        task.save()
        self.assertEqual(20, self.job.progress)
        task.variant_group = 1
        task.variant_serial = 1
        task.save()
        self.assertEqual(20, self.job.progress)


class TestJobTransitions(TestCase):

    def setUp(self):
        activate('en')
        self.company = CompanyFactory()
        self.project = ProjectFactory()
        self.job = JobFactory(project=self.project)
        self.letterhead = LetterheadFactory()

    def test_job_draft(self):
        self.assertEquals('Draft', self.job.get_status_display())

    def test_job_proposed(self):
        proposal = ProposalFactory(project=self.project, letterhead=self.letterhead)
        proposal.jobs.add(self.job)
        self.job.refresh_from_db()
        self.assertEquals('Proposed', self.job.get_status_display())

    def test_job_approved(self):
        proposal = ProposalFactory(project=self.project, letterhead=self.letterhead)
        proposal.jobs.add(self.job)
        proposal.send()
        proposal.approve()
        self.job.refresh_from_db()
        self.assertEquals('Approved', self.job.get_status_display())

    def test_job_declined(self):
        proposal = ProposalFactory(project=self.project, letterhead=self.letterhead)
        proposal.jobs.add(self.job)
        self.job.refresh_from_db()
        self.assertEquals('Proposed', self.job.get_status_display())
        proposal.send()
        proposal.decline()
        self.job.refresh_from_db()
        self.assertEquals('Draft', self.job.get_status_display())

    def test_job_after_proposal_deleted(self):
        proposal = ProposalFactory(project=self.project, letterhead=self.letterhead)
        proposal.jobs.add(self.job)
        self.job.refresh_from_db()
        self.assertEquals('Proposed', self.job.get_status_display())
        proposal.delete()
        self.job.refresh_from_db()
        self.assertEquals('Draft', self.job.get_status_display())


class CodeFormattingTests(TestCase):

    def setUp(self):
        CompanyFactory()

    def test_job_code(self):
        project = ProjectFactory(structure_format="0.0")
        self.assertEqual(JobFactory(project=project).code, '1')
        self.assertEqual(JobFactory(project=project).code, '2')
        project = ProjectFactory(structure_format="000.0")
        self.assertEqual(JobFactory(project=project).code, '001')
        self.assertEqual(JobFactory(project=project).code, '002')

    def test_group_code(self):
        job = JobFactory(project=ProjectFactory(structure_format="0.000.00.0"))
        group = GroupFactory(parent=job)
        self.assertEqual(group.code, '1.001')
        self.assertEqual(GroupFactory(parent=group).code, '1.001.01')
        self.assertEqual(GroupFactory(parent=group).code, '1.001.02')
        group = GroupFactory(parent=job)
        self.assertEqual(GroupFactory(parent=group).code, '1.002.01')
        self.assertEqual(GroupFactory(parent=group).code, '1.002.02')

    def test_job_direct_tasks_code(self):
        """ Tasks are attached directly to the job. """
        job = JobFactory(project=ProjectFactory(structure_format="00.000"))
        task = TaskFactory(group=job)
        self.assertEqual(task.code, '01.001')

    def test_blank_group_task_code(self):
        """ One of the groups in the hierarchy is blank. """
        job = JobFactory(project=ProjectFactory(structure_format="00.00.000"))
        group = GroupFactory(name='', parent=job)
        task = TaskFactory(group=group)
        self.assertEqual(task.code, '01._.001')

    def test_complex_groups_task_code(self):
        """ A more comprehensive test case. """
        job = JobFactory(project=ProjectFactory(structure_format="0.00.00.0000"))
        group1 = GroupFactory(parent=job)
        GroupFactory(parent=group1)
        GroupFactory(parent=group1)
        group2 = GroupFactory(parent=group1)
        TaskFactory(group=group2)
        task = TaskFactory(group=group2)
        self.assertEqual(task.code, "1.01.03.0002")


class CloningTests(TestCase):

    def setUp(self):
        CompanyFactory()

    def test_clone(self):
        job = JobFactory(project=ProjectFactory())
        group = GroupFactory(name="my group", parent=job)
        TaskFactory(group=group)
        TaskFactory(group=group)
        TaskFactory(
            name="running task",
            group=GroupFactory(parent=job),
            qty=7, complete=7, status=Task.RUNNING,
            started_on=datetime.date.today(),
            completed_on=datetime.date.today()
        )

        new_job = JobFactory(project=ProjectFactory())
        self.assertEqual(new_job.groups.count(), 0)
        self.assertEqual(new_job.all_tasks.count(), 0)

        job.clone_to(new_job)
        self.assertEqual(new_job.groups.count(), 2)
        self.assertEqual(new_job.all_tasks.count(), 3)

        new_group = new_job.groups.first()
        self.assertEqual(new_group.tasks.count(), 2)
        self.assertEqual(group.name, new_group.name)
        self.assertNotEqual(group.pk, new_group.pk)

        new_task = new_job.groups.all()[1].tasks.first()
        self.assertEqual(new_task.name, "running task")
        self.assertEqual(new_task.complete, 0)
        self.assertEqual(new_task.status, '')
        self.assertIsNone(new_task.started_on)
        self.assertIsNone(new_task.completed_on)

        # TODO: Test what happens when heterogeneous structured objects
        #       are cloned, cloning should either truncate the larger
        #       structure or pad a smaller structure to make it fit.
        # TODO: Test that correction lineitems don't get copied.


class GenerateGroupsTests(TestCase):

    def setUp(self):
        CompanyFactory()

    def test_no_groups_to_generate_for_job(self):
        project = ProjectFactory(structure_format="0.0")
        job = JobFactory(project=project)
        self.assertEqual(Group.objects.count(), 1)
        job.generate_groups()
        self.assertEqual(Group.objects.count(), 1)

    def test_two_subgroups_generated_from_job(self):
        project = ProjectFactory(structure_format="0.0.0.0")
        job = JobFactory(project=project)
        self.assertEqual(Group.objects.count(), 1)
        job.generate_groups()
        self.assertEqual(Group.objects.count(), 3)
        self.assertEqual(job.root.pk, 1)
        self.assertEqual(job.groups.first().pk, 2)
        self.assertEqual(job.groups.first().groups.first().pk, 3)


class GroupPrefetchingTests(TestCase):

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

