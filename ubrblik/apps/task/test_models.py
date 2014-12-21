from django.test import TestCase
from django.contrib.auth import get_user_model
from ..project.models import *
from .models import *

User = get_user_model()


def create_task_data(self):
    self.user = User.objects.create_user('lex', 'lex@damoti.com', 'pass')
    self.project = Project.objects.create(name="my project")
    self.project2 = Project.objects.create(name="my project 2")
    self.job = Job.objects.create(name="Default", project=self.project)
    self.group = TaskGroup.objects.create(name="my group", job=self.job)
    self.group2 = TaskGroup.objects.create(name="my group 2", job=self.job)
    self.task = Task.objects.create(name="my task", qty=0, taskgroup=self.group)
    self.lineitem = LineItem.objects.create(name="my task", qty=8, price=120, task=self.task)
    self.task2 = Task.objects.create(name="my task", qty=0, taskgroup=self.group)
    self.lineitem2 = LineItem.objects.create(name="my task", qty=0, price=0, task=self.task2)


class TaskTotalTests(TestCase):

    def setUp(self):
        create_task_data(self)
    
    def test_zero_total(self):
        task = Task.objects.get(pk=self.task2.pk)
        self.assertEqual(0, task.total_amount)

    def test_non_zero_total(self):
        lineitem1 = LineItem.objects.create(name="do stuff", price=10, qty=8, unit="hour", task=self.task)
        self.assertEqual(80, lineitem1.total_amount)
        task = Task.objects.get(pk=self.task.pk)
        self.assertEqual(1040, task.total_amount)