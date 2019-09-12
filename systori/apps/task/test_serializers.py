from decimal import Decimal

from django.urls import reverse

from systori.lib.testing import ClientTestCase

from systori.apps.project.factories import ProjectFactory, JobSiteFactory
from systori.apps.task.factories import (
    GroupFactory,
    JobFactory,
    LineItemFactory,
    TaskFactory,
)
from systori.apps.task.models import Group, LineItem, Task
from systori.apps.task.serializers import TaskSerializer, GroupSerializer


class TaskSerializerTest(ClientTestCase):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.jobsite = JobSiteFactory(project=self.project)

    def test_can_serialize_task_from_job(self):
        job = JobFactory(project=self.project)
        task = TaskFactory(group=job, price=5, complete=10, total=100)

        serializer = TaskSerializer(instance=task)
        serialized = serializer.data

        self.assertDictContainsSubset(serialized, {"price": 5, "total": 100})

    def test_can_serialize_task_with_lineitems_from_job(self):
        job = JobFactory(project=self.project)
        task = TaskFactory(group=job, price=5, complete=10, total=100)

        LineItemFactory(name="Clean celing", unit="hr", qty=8, price=12, task=task)
        LineItemFactory(name="Clean floor", unit="hr", qty=4, price=26, task=task)
        LineItemFactory(name="Clean doors", unit="hr", qty=4, price=20, task=task)

        serializer = TaskSerializer(instance=task)
        serialized = serializer.data

        self.assertDictContainsSubset(serialized, {"price": 5, "total": 100})

        self.assertDictContainsSubset(
            serialized["lineitems"][0],
            {"name": "Clean celing", "unit": "hr", "qty": 8, "price": 12},
        )
        self.assertDictContainsSubset(
            serialized["lineitems"][1],
            {"name": "Clean floor", "unit": "hr", "qty": 4, "price": 26},
        )
        self.assertDictContainsSubset(
            serialized["lineitems"][2],
            {"name": "Clean doors", "unit": "hr", "qty": 4, "price": 20},
        )

    def test_can_serialize_task_with_lineitems_from_group(self):
        job = JobFactory(project=self.project)
        group = GroupFactory(name="test group", description="desc", job=job)
        task = TaskFactory(
            name="Cleaning", group=group, qty=1, total=1, description="clean stuff"
        )
        LineItemFactory(name="Clean celing", unit="hr", qty=8, price=12, task=task)
        LineItemFactory(name="Clean floor", unit="hr", qty=4, price=26, task=task)
        LineItemFactory(name="Clean doors", unit="hr", qty=4, price=20, task=task)

        serializer = TaskSerializer(instance=task)
        serialized = serializer.data

        self.assertDictContainsSubset(
            serialized,
            {"name": "Cleaning", "qty": 1, "total": 1, "description": "clean stuff"},
        )

        self.assertDictContainsSubset(
            serialized["lineitems"][0],
            {"name": "Clean celing", "unit": "hr", "qty": 8, "price": 12},
        )
        self.assertDictContainsSubset(
            serialized["lineitems"][1],
            {"name": "Clean floor", "unit": "hr", "qty": 4, "price": 26},
        )
        self.assertDictContainsSubset(
            serialized["lineitems"][2],
            {"name": "Clean doors", "unit": "hr", "qty": 4, "price": 20},
        )


class GroupSerializerTest(ClientTestCase):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.jobsite = JobSiteFactory(project=self.project)

    def test_can_serialize_group_with_no_tasks(self):
        job = JobFactory(project=self.project)
        group = GroupFactory(name="test group", description="desc", job=job)

        serializer = GroupSerializer(instance=group)
        serialized = serializer.data

        self.assertDictContainsSubset(
            serialized,
            {"name": "test group", "description": "desc", "groups": [], "tasks": []},
        )

    def test_can_serialize_group_with_tasks(self):
        job = JobFactory(project=self.project)
        group = GroupFactory(name="test group", description="desc", job=job)
        task = TaskFactory(
            name="Cleaning", group=group, qty=1, total=1, description="clean stuff"
        )

        serializer = GroupSerializer(instance=group)
        serialized = serializer.data

        self.assertDictContainsSubset(
            serialized, {"name": "test group", "description": "desc", "groups": []}
        )
        self.assertDictContainsSubset(
            serialized["tasks"][0],
            {"name": "Cleaning", "qty": 1, "total": 1, "description": "clean stuff"},
        )

    def test_can_serialize_group_with_sub_group_with_tasks(self):
        project = ProjectFactory(structure="01.01.01.001")
        job = JobFactory(project=project)
        group = GroupFactory(name="test group", description="desc", job=job)

        sub_group = GroupFactory(name="sub group", description="desc", parent=group)

        sub_group_task = TaskFactory(
            name="Cleaning 2",
            group=sub_group,
            qty=1,
            total=1,
            description="clean stuff again",
        )

        serializer = GroupSerializer(instance=group)
        serialized = serializer.data

        self.assertDictContainsSubset(
            serialized, {"name": "test group", "description": "desc", "tasks": []}
        )
        self.assertDictContainsSubset(
            serialized["groups"][0], {"name": "sub group", "description": "desc"}
        )
        self.assertDictContainsSubset(
            serialized["groups"][0]["tasks"][0],
            {
                "name": "Cleaning 2",
                "qty": 1,
                "total": 1,
                "description": "clean stuff again",
            },
        )
