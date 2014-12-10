from django.test import TestCase
from django.contrib.auth import get_user_model
from ..project.models import *
from ..task.models import *
from .models import *


class DocumentTests(TestCase):

    def setUp(self):
        self.proj = Project.objects.create(name="my project")
        group = TaskGroup.objects.create(name="my group", project=self.proj)
        self.task = Task.objects.create(name="my task", taskgroup=group)

    def test_associate_task(self):
        p = Document.objects.create(project=self.proj)

        p.add_task(self.task)

        p = Document.objects.get(pk=p.pk)
        self.assertEquals(1, p.items.count())