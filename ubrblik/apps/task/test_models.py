from django.test import TestCase
from django.contrib.auth import get_user_model
from ..project.models import *
from .models import *

User = get_user_model()


def create_data(self):
    self.user = User.objects.create_user('lex', 'lex@damoti.com', 'pass')
    self.proj = Project.objects.create(name="my project")
    self.group = TaskGroup.objects.create(name="my group", project=self.proj)
    self.group2 = TaskGroup.objects.create(name="my group 2", project=self.proj)
    self.task = Task.objects.create(name="my task", taskgroup=self.group)
    self.lineitem = LineItem.objects.create(name="my task", qty=0, price=0, task=self.task)


class TaskTotalTests(TestCase):

    def setUp(self):
        create_data(self)
    
    def test_zero(self):
        task = Task.objects.get(pk=self.task.pk)
        self.assertEqual(0, task.total)

    def test_lineitem_total(self):
        lineitem1 = LineItem.objects.create(name="do stuff", price=10, qty=8, unit="hour", task=self.task)
        lineitem2 = LineItem.objects.create(name="do more", price=20, qty=8, unit="hour", task=self.task)
        self.assertEqual(80, lineitem1.total)

        task = Task.objects.get(pk=self.task.pk)
        self.assertEqual(240, task.total)