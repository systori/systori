from django.test import TestCase
from django.contrib.auth import get_user_model
from ..task.models import *
from .models import *

User = get_user_model()


def create_data(self):
    self.user = User.objects.create_user('lex', 'lex@damoti.com', 'pass')
    self.proj = Project.objects.create(name="my project")
    self.proj2 = Project.objects.create(name="my second project")
    self.group = TaskGroup.objects.create(name="my group", project=self.proj)
    self.group2 = TaskGroup.objects.create(name="my group 2", project=self.proj)
    self.task = Task.objects.create(name="my task", taskgroup=self.group)
    self.lineitem = LineItem.objects.create(name="my task", qty=8, price=120, task=self.task)


class ProjectTotalTests(TestCase):

    def setUp(self):
        create_data(self)
    
    def test_zero(self):
        project = Project.objects.get(pk=self.proj2.pk)
        self.assertEqual(0, project.total)
        self.assertEqual(0, project.tax)
        self.assertEqual(0, project.total_gross)

    def test_nonzero(self):
        project = Project.objects.get(pk=self.proj.pk)
        self.assertEqual(960, project.total)
        self.assertEqual(182.4, float(round(project.tax, 1)))
        self.assertEqual(1142.4, float(round(project.total_gross, 1)))