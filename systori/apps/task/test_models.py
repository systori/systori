import datetime
from django.test import TestCase
from django.utils.translation import activate

from ..project.models import Project
from ..project.factories import ProjectFactory
from ..company.factories import CompanyFactory
from ..document.factories import ProposalFactory, LetterheadFactory

from .factories import JobFactory, GroupFactory, TaskFactory, LineItemFactory
from .models import Job, Group, Task


class CalculationTests(TestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.project = ProjectFactory()
        self.job = JobFactory(project=self.project)
        self.group = GroupFactory(parent=self.job)

    def check_totals(self, estimate=0, progress=0, is_billable=False, num_queries=10):

        with self.assertNumQueries(num_queries):
            job = Job.objects.get(id=self.job.id)
            self.assertEqual(job.estimate, estimate)
            self.assertEqual(job.progress, progress)
            self.assertEqual(job.is_billable, is_billable)

        with self.assertNumQueries(1):
            job = Job.objects.with_is_billable().get(id=self.job.id)
            self.assertEqual(job.is_billable, is_billable)

        with self.assertNumQueries(1):
            job = Job.objects.with_totals().get(id=self.job.id)
            self.assertEqual(job.estimate, estimate)
            self.assertEqual(job.progress, progress)

        with self.assertNumQueries(1):
            project = Project.objects.with_totals().get(id=self.project.id)
            self.assertEqual(project.estimate, estimate)
            self.assertEqual(project.progress, progress)

    def test_task_zero(self):
        task = TaskFactory(group=self.group)
        self.assertEqual(task.total, 0)
        self.assertEqual(task.progress, 0)
        self.assertEqual(self.group.estimate, 0)
        self.assertEqual(self.group.progress, 0)
        self.check_totals()

    def test_task_with_progress(self):
        task = TaskFactory(group=self.group, qty=5, complete=3, price=8)
        self.assertTrue(task.is_billable)
        self.assertEqual(task.progress, 24)
        self.assertEqual(task.complete_percent, 60)
        self.check_totals(0, 24, True)

    def test_blank_task_price_difference(self):
        """ To prevent regression, used to throw:
            TypeError: unsupported operand type(s) for -: 'float' and 'decimal.Decimal'
        """
        task = Task()  # type: Task
        self.assertEqual(task.price_difference, 0)

    def test_task_price_difference(self):
        task = TaskFactory(group=self.job, price=0)  # type: Task
        LineItemFactory(task=task, total=10)
        self.assertTrue(task.price_difference, 2)

    def test_task_estimate_determination(self):
        task = TaskFactory(group=self.group, total=99)
        self.assertEqual(task.include_estimate, True)
        self.check_totals(99)

    def test_task_estimate_determination_is_provisional(self):
        task = TaskFactory(group=self.group, is_provisional=True, total=99)
        self.assertEqual(task.include_estimate, False)
        self.check_totals(0)

    def test_task_estimate_determination_variants(self):
        task = TaskFactory(group=self.group, variant_group=1, total=99)
        self.assertEqual(task.include_estimate, True)
        self.check_totals(99)
        task.variant_serial = 1
        task.save()
        self.assertEqual(task.include_estimate, False)
        self.check_totals(0)

    def test_task_progress_unaffected_by_task_states(self):
        """ Progress from completion is always counted regardless of is_provisional or variant serial."""
        task = TaskFactory(group=self.job, complete=2, price=10)
        self.assertEqual(task.progress, 20)
        self.check_totals(0, 20, True)

        task.is_provisional = True
        task.save()
        self.assertEqual(task.progress, 20)
        self.check_totals(0, 20, True)

        task.variant_group = 1
        task.variant_serial = 1
        task.save()
        self.assertEqual(task.progress, 20)
        self.check_totals(0, 20, True)

    def test_complete_percent(self):
        # Division by zero
        self.assertEqual(TaskFactory(group=self.job, complete=10, qty=0).complete_percent, 0)
        # Complete greater than qty
        self.assertEqual(TaskFactory(group=self.job, complete=10, qty=5).complete_percent, 200)
        # 100% rounding
        self.assertEqual(TaskFactory(group=self.job, complete=99.99, qty=100).complete_percent, 100)
        self.assertEqual(TaskFactory(group=self.job, complete=100.01, qty=100).complete_percent, 100)

    def test_group_with_tasks(self):
        TaskFactory(group=self.group, total=7)
        TaskFactory(group=self.group, total=8)
        self.check_totals(15)

    def test_multiple_subgroups(self):
        TaskFactory(group=self.group, total=7)
        group = GroupFactory(parent=self.job)
        TaskFactory(group=group, total=8)
        self.assertEqual(7, self.group.estimate)
        self.assertEqual(8, group.estimate)
        job = Job.objects.with_totals().get(pk=self.job)
        self.assertEqual(15, job.estimate)


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


class GroupTests(TestCase):

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

    def test_prefetching(self):
        project = ProjectFactory(structure_format="0.00.00.00.00.0000")
        job = JobFactory(project=project)  # type: Job
        job.generate_groups()

        group = GroupFactory(parent=job)  # type: Group
        group.generate_groups()

        leaf_group1 = job.groups.first().groups.first().groups.first().groups.first()
        leaf_group2 = group.groups.first().groups.first().groups.first()

        LineItemFactory(name='the lineitem', task=TaskFactory(group=leaf_group1))
        LineItemFactory(name='the lineitem', task=TaskFactory(group=leaf_group2))

        def traverse_children(group, depth=0):
            if depth == 4:
                for task in group.tasks.all():
                    for lineitem in task.lineitems.all():
                        return lineitem
                return

            result = None
            for subgroup in group.groups.all():
                result = traverse_children(subgroup, depth+1)

            return result

        # no prefetch
        with self.assertNumQueries(12):
            self.assertIsNotNone(traverse_children(
                Job.objects.get(pk=job.pk)
            ))

        # with prefetch
        with self.assertNumQueries(7):
            self.assertIsNotNone(traverse_children(
                Job.objects.with_hierarchy(project).get(pk=job.pk)
            ))
