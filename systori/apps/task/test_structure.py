import datetime
from django.test import TestCase
from ..company.factories import *
from ..project.factories import *
from ..task.factories import *
from ..user.factories import *


def create_data(self):
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
        self.assertEqual(new_job.alltasks.count(), 0)

        job.clone_to(new_job)
        self.assertEqual(new_job.groups.count(), 2)
        self.assertEqual(new_job.alltasks.count(), 3)

        new_group = new_job.groups.first()
        self.assertEqual(new_group.tasks.count(), 2)
        self.assertEqual(group.name, new_group.name)
        self.assertNotEqual(group.pk, new_group.pk)

        new_task = new_job.groups.all()[1].tasks.first()
        self.assertEqual(new_task.name, "running task")
        self.assertEqual(new_task.qty, 0)
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

