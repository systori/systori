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
    self.task = Task.objects.create(name="my task", group=self.group)


class TaskTotalTests(TestCase):

    def setUp(self):
        create_data(self)
    
    def test_zero(self):
        task = Task.objects.get(pk=self.task.pk)
        self.assertEqual(0, task.total)

    def test_labor_total(self):
        labor1 = Labor.objects.create(name="do stuff", cost=10, qty=8, unit="hour", task=self.task)
        labor2 = Labor.objects.create(name="do more", cost=20, qty=8, unit="hour", task=self.task)
        self.assertEqual(80, labor1.total)

        task = Task.objects.get(pk=self.task.pk)
        self.assertEqual(240, task.total)

    def test_material_total(self):
        material1 = Material.objects.create(name="stuff", cost=5, qty=100, unit="m", task=self.task)
        material2 = Material.objects.create(name="lumber", cost=2, qty=300, unit="m", task=self.task)
        self.assertEqual(500, material1.total)

        task = Task.objects.get(pk=self.task.pk)
        self.assertEqual(1100, task.total)

    def test_hybrid_total(self):
        Labor.objects.create(name="do stuff", cost=10, qty=8, unit="hour", task=self.task)
        Material.objects.create(name="stuff", cost=5, qty=100, unit="m", task=self.task)
        task = Task.objects.get(pk=self.task.pk)
        self.assertEqual(580, task.total)