from django.test import TestCase
from django.contrib.auth import get_user_model
from ..task.models import *
from .models import *

from ..task.test_models import create_task_data

User = get_user_model()


class ProjectTotalTests(TestCase):

    def setUp(self):
        create_task_data(self)
    
    def test_zero(self):
        project = Project.objects.get(pk=self.project2.pk)
        self.assertEqual(0, project.total)
        self.assertEqual(0, project.tax)
        self.assertEqual(0, project.total_gross)

    def test_nonzero(self):
        project = Project.objects.get(pk=self.project.pk)
        self.assertEqual(960, project.total)
        self.assertEqual(182.4, float(round(project.tax, 1)))
        self.assertEqual(1142.4, float(round(project.total_gross, 1)))