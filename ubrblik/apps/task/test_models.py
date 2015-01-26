from django.test import TestCase
from django.contrib.auth import get_user_model
from ..project.models import *
from .models import *

User = get_user_model()


def create_task_data(self):
    self.user = User.objects.create_user('lex', 'lex@damoti.com', 'pass')
    self.template_project = Project.objects.create(name="Template Project", is_template=True)
    self.project = Project.objects.create(name="my project")
    self.project2 = Project.objects.create(name="my project 2")
    self.job = Job.objects.create(name="Default", project=self.project)
    self.group = TaskGroup.objects.create(name="my group", job=self.job)
    self.group2 = TaskGroup.objects.create(name="my group 2", job=self.job)
    self.task = Task.objects.create(name="my task one", qty=1, taskgroup=self.group)
    TaskInstance.objects.create(task=self.task,selected=True)
    self.lineitem = LineItem.objects.create(name="my line item 1", unit_qty=8, price=120, taskinstance=self.task.instance)
    self.task2 = Task.objects.create(name="my task two", qty=0, taskgroup=self.group)
    TaskInstance.objects.create(task=self.task2,selected=True)
    self.lineitem2 = LineItem.objects.create(name="my line item 2", unit_qty=0, price=0, taskinstance=self.task2.instance)


class TaskInstanceTotalTests(TestCase):

    def setUp(self):
        create_task_data(self)
    
    def test_zero_total(self):
        task = TaskInstance.objects.get(pk=self.task2.instance.pk)
        self.assertEqual(0, task.fixed_price_estimate)
        self.assertEqual(0, task.fixed_price_billable)
        self.assertEqual(0, task.time_and_materials_estimate)
        self.assertEqual(0, task.time_and_materials_billable)

    def test_non_zero_total(self):
        lineitem1 = LineItem.objects.create(name="do stuff", price=10, unit_qty=8, unit="hour", taskinstance=self.task.instance)
        self.assertEqual(80, lineitem1.price_per_task_unit)
        task = TaskInstance.objects.get(pk=self.task.instance.pk)
        self.assertEqual(1040, task.fixed_price_estimate)


class JobTotalTests(TestCase):

    def setUp(self):
        create_task_data(self)
        self.job2 = Job.objects.create(name="Empty Job", project=self.project)
    
    def test_zero_total(self):
        jobs = Job.objects.filter(pk=self.job2.id)
        self.assertEqual(0, jobs.estimate_total())
        self.assertEqual(0, jobs.estimate_tax_total())
        self.assertEqual(0, jobs.estimate_gross_total())
        self.assertEqual(0, jobs.billable_total())
        self.assertEqual(0, jobs.billable_tax_total())
        self.assertEqual(0, jobs.billable_gross_total())

    def test_nonzero_total(self):
        jobs = Job.objects
        self.assertEqual(Decimal(960), jobs.estimate_total())
        self.assertEqual(Decimal(0), jobs.billable_total())
        self.assertEqual(round(Decimal(960*.19),2), round(jobs.estimate_tax_total(),2))
        self.assertEqual(round(Decimal(960*1.19),2), round(jobs.estimate_gross_total(),2))


class TaskCloneTests(TestCase):

    def setUp(self):
        create_task_data(self)

    def test_clone(self):
        new_job = Job.objects.create(name="New", project=self.project)
        self.assertEqual(new_job.taskgroups.count(), 0)
        self.job.clone_to(new_job)

        job = Job.objects.get(pk=new_job.pk)
        self.assertEqual(job.taskgroups.count(), 2)
        group = job.taskgroups.get(name="my group")
        self.assertNotEqual(group.id, self.group.id)
        self.assertEqual(group.tasks.count(), 2)