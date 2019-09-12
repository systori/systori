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
        # Has structure 01.01.001
        self.project = ProjectFactory()
        self.jobsite = JobSiteFactory(project=self.project)

    def test_can_serialize_task_from_job(self):
        job = JobFactory(project=self.project)
        task = TaskFactory(group=job, price=5, complete=10, total=100)

        serializer = TaskSerializer(instance=task)
        serialized = serializer.data

        self.assertDictContainsSubset({"price": "5.00", "total": "100.00"}, serialized)

    def test_can_serialize_task_from_group_from_job(self):
        job = JobFactory(project=self.project)
        group = GroupFactory(name="test group", description="desc", parent=job, depth=1)
        task = TaskFactory(
            name="Cleaning", group=group, qty=1, total=1, description="clean stuff"
        )
        serializer = TaskSerializer(instance=task)
        serialized = serializer.data

        self.assertDictContainsSubset(
            {"name": "Cleaning", "qty": "1.000", "total": "1.00", "description": "clean stuff"},
            serialized,
        )

    def test_can_serialize_task_from_subgroup_from_group_from_job(self):
        project = ProjectFactory(structure="01.01.01.001")
        job = JobFactory(project=project)
        group = GroupFactory(name="test group", description="desc", parent=job, depth=1)
        sub_group = GroupFactory(name="test sub group", description="desc", parent=group)
        task = TaskFactory(
            name="Cleaning", group=sub_group, qty=1, total=1, description="clean stuff"
        )
        serializer = TaskSerializer(instance=task)
        serialized = serializer.data

        self.assertDictContainsSubset(
            {"name": "Cleaning", "qty": "1.000", "total": "1.00", "description": "clean stuff"},
            serialized,
        )

    def test_can_serialize_task_with_lineitems_from_job(self):
        job = JobFactory(project=self.project)
        task = TaskFactory(group=job, price=5, complete=10, total=100)

        LineItemFactory(name="Clean celing", unit="hr", qty=8, price=12, task=task)
        LineItemFactory(name="Clean floor", unit="hr", qty=4, price=26, task=task)
        LineItemFactory(name="Clean doors", unit="hr", qty=4, price=20, task=task)

        serializer = TaskSerializer(instance=task)
        serialized = serializer.data

        self.assertDictContainsSubset({"price": "5.00", "total": "100.00"}, serialized)

        self.assertDictContainsSubset(
            {"name": "Clean celing", "unit": "hr", "qty": "8.000", "price": "12.00"},
            serialized["lineitems"][0],
        )
        self.assertDictContainsSubset(
            {"name": "Clean floor", "unit": "hr", "qty": "4.000", "price": "26.00"},
            serialized["lineitems"][1],
        )
        self.assertDictContainsSubset(
            {"name": "Clean doors", "unit": "hr", "qty": "4.000", "price": "20.00"},
            serialized["lineitems"][2],
        )

    def test_can_serialize_task_with_lineitems_from_group(self):
        job = JobFactory(project=self.project)
        group = GroupFactory(name="test group", description="desc", parent=job, depth=1)
        task = TaskFactory(
            name="Cleaning", group=group, qty=1, total=1, description="clean stuff"
        )
        LineItemFactory(name="Clean celing", unit="hr", qty=8, price=12, task=task)
        LineItemFactory(name="Clean floor", unit="hr", qty=4, price=26, task=task)
        LineItemFactory(name="Clean doors", unit="hr", qty=4, price=20, task=task)

        serializer = TaskSerializer(instance=task)
        serialized = serializer.data

        self.assertDictContainsSubset(
            {"name": "Cleaning", "qty": "1.000", "total": "1.00", "description": "clean stuff"},
            serialized,
        )

        self.assertDictContainsSubset(
            {"name": "Clean celing", "unit": "hr", "qty": "8.000", "price": "12.00"},
            serialized["lineitems"][0],
        )
        self.assertDictContainsSubset(
            {"name": "Clean floor", "unit": "hr", "qty": "4.000", "price": "26.00"},
            serialized["lineitems"][1],
        )
        self.assertDictContainsSubset(
            {"name": "Clean doors", "unit": "hr", "qty": "4.000", "price": "20.00"},
            serialized["lineitems"][2],
        )

    def test_can_serialize_task_with_lineitems_from_subgroup_from_group_from_job(self):
        project = ProjectFactory(structure="01.01.01.001")
        job = JobFactory(project=project)
        group = GroupFactory(name="test group", description="desc", parent=job, depth=1)
        sub_group = GroupFactory(name="test sub group", description="desc", parent=group)

        sub_group_task = TaskFactory(
            name="Cleaning", group=sub_group, qty=1, total=1, description="clean stuff"
        )

        LineItemFactory(
            name="Clean celing", unit="hr", qty=8, price=12, task=sub_group_task
        )
        LineItemFactory(
            name="Clean floor", unit="hr", qty=4, price=26, task=sub_group_task
        )
        LineItemFactory(
            name="Clean doors", unit="hr", qty=4, price=20, task=sub_group_task
        )
        serializer = TaskSerializer(instance=sub_group_task)
        serialized = serializer.data

        self.assertDictContainsSubset(
            {"name": "Cleaning", "qty": "1.000", "total": "1.00", "description": "clean stuff"},
            serialized,
        )

        self.assertDictContainsSubset(
            {"name": "Clean celing", "unit": "hr", "qty": "8.000", "price": "12.00"},
            serialized["lineitems"][0],
        )
        self.assertDictContainsSubset(
            {"name": "Clean floor", "unit": "hr", "qty": "4.000", "price": "26.00"},
            serialized["lineitems"][1],
        )
        self.assertDictContainsSubset(
            {"name": "Clean doors", "unit": "hr", "qty": "4.000", "price": "20.00"},
            serialized["lineitems"][2],
        )


class GroupSerializerTest(ClientTestCase):
    def setUp(self):
        super().setUp()
        # Has structure 01.01.001
        self.project = ProjectFactory()
        self.jobsite = JobSiteFactory(project=self.project)

    def test_can_serialize_group_with_no_tasks(self):
        job = JobFactory(project=self.project)
        group = GroupFactory(name="test group", description="desc", parent=job, depth=1)

        serializer = GroupSerializer(instance=group)
        serialized = serializer.data

        self.assertDictContainsSubset(
            {"name": "test group", "description": "desc", "groups": [], "tasks": []},
            serialized,
        )

    def test_can_serialize_group_with_tasks(self):
        job = JobFactory(project=self.project)
        group = GroupFactory(name="test group", description="desc", parent=job, depth=1)
        task = TaskFactory(
            name="Cleaning", group=group, qty=1, total=1, description="clean stuff"
        )

        serializer = GroupSerializer(instance=group)
        serialized = serializer.data

        self.assertDictContainsSubset(
            {"name": "test group", "description": "desc", "groups": []}, serialized
        )
        self.assertDictContainsSubset(
            {"name": "Cleaning", "qty": "1.000", "total": "1.00", "description": "clean stuff"},
            serialized["tasks"][0],
        )

    def test_can_serialize_group_with_tasks_with_lineitems(self):
        job = JobFactory(project=self.project)
        group = GroupFactory(name="test group", description="desc", parent=job, depth=1)
        task = TaskFactory(
            name="Cleaning", group=group, qty=1, total=1, description="clean stuff"
        )
        LineItemFactory(name="Clean celing", unit="hr", qty=8, price=12, task=task)
        LineItemFactory(name="Clean floor", unit="hr", qty=4, price=26, task=task)
        LineItemFactory(name="Clean doors", unit="hr", qty=4, price=20, task=task)

        serializer = GroupSerializer(instance=group)
        serialized = serializer.data

        self.assertDictContainsSubset(
            {"name": "test group", "description": "desc", "groups": []}, serialized
        )
        self.assertDictContainsSubset(
            {"name": "Cleaning", "qty": "1.000", "total": "1.00", "description": "clean stuff"},
            serialized["tasks"][0],
        )
        self.assertDictContainsSubset(
            {"name": "Clean celing", "unit": "hr", "qty": "8.000", "price": "12.00"},
            serialized["tasks"][0]["lineitems"][0],
        )
        self.assertDictContainsSubset(
            {"name": "Clean floor", "unit": "hr", "qty": "4.000", "price": "26.00"},
            serialized["tasks"][0]["lineitems"][1],
        )
        self.assertDictContainsSubset(
            {"name": "Clean doors", "unit": "hr", "qty": "4.000", "price": "20.00"},
            serialized["tasks"][0]["lineitems"][2],
        )

    def test_can_serialize_group_with_sub_group_with_no_tasks(self):
        project = ProjectFactory(structure="01.01.01.001")
        job = JobFactory(project=project)
        group = GroupFactory(name="test group", description="desc", parent=job, depth=1)

        sub_group = GroupFactory(
            name="sub group", description="desc", parent=group, depth=2
        )

        serializer = GroupSerializer(instance=group)
        serialized = serializer.data

        self.assertDictContainsSubset(
            {"name": "test group", "description": "desc", "tasks": []}, serialized
        )
        self.assertDictContainsSubset(
            {"name": "sub group", "description": "desc", "tasks": []},
            serialized["groups"][0],
        )

    def test_can_serialize_group_with_sub_group_with_tasks(self):
        project = ProjectFactory(structure="01.01.01.001")
        job = JobFactory(project=project)
        group = GroupFactory(name="test group", description="desc", parent=job, depth=1)

        sub_group = GroupFactory(
            name="sub group", description="desc", parent=group, depth=2
        )

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
            {"name": "test group", "description": "desc", "tasks": []}, serialized
        )
        self.assertDictContainsSubset(
            {"name": "sub group", "description": "desc"}, serialized["groups"][0]
        )
        self.assertDictContainsSubset(
            {
                "name": "Cleaning 2",
                "qty": 1,
                "total": 1,
                "description": "clean stuff again",
            },
            serialized["groups"][0]["tasks"][0],
        )

    def test_can_serialize_group_with_sub_group_with_tasks_with_lineitems(self):
        project = ProjectFactory(structure="01.01.01.001")
        job = JobFactory(project=project)
        group = GroupFactory(name="test group", description="desc", parent=job, depth=1)

        sub_group = GroupFactory(
            name="sub group", description="desc", parent=group, depth=2
        )

        sub_group_task = TaskFactory(
            name="Cleaning 2",
            group=sub_group,
            qty=1,
            total=1,
            description="clean stuff again",
        )

        LineItemFactory(
            name="Clean celing", unit="hr", qty=8, price=12, task=sub_group_task
        )
        LineItemFactory(
            name="Clean floor", unit="hr", qty=4, price=26, task=sub_group_task
        )
        LineItemFactory(
            name="Clean doors", unit="hr", qty=4, price=20, task=sub_group_task
        )

        serializer = GroupSerializer(instance=group)
        serialized = serializer.data

        self.assertDictContainsSubset(
            {"name": "test group", "description": "desc", "tasks": []}, serialized
        )
        self.assertDictContainsSubset(
            {"name": "sub group", "description": "desc"}, serialized["groups"][0]
        )
        self.assertDictContainsSubset(
            {
                "name": "Cleaning 2",
                "qty": 1,
                "total": 1,
                "description": "clean stuff again",
            },
            serialized["groups"][0]["tasks"][0],
        )
        self.assertDictContainsSubset(
            {"name": "Clean celing", "unit": "hr", "qty": "8.000", "price": "12.00"},
            serialized["groups"][0]["tasks"][0]["lineitems"][0],
        )
        self.assertDictContainsSubset(
            {"name": "Clean floor", "unit": "hr", "qty": "4.000", "price": "26.00"},
            serialized["groups"][0]["tasks"][0]["lineitems"][1],
        )
        self.assertDictContainsSubset(
            {"name": "Clean doors", "unit": "hr", "qty": "4.000", "price": "20.00"},
            serialized["groups"][0]["tasks"][0]["lineitems"][2],
        )

    def test_can_serialize_group_with_sub_group_with_sub_group_with_no_tasks(self):
        project = ProjectFactory(structure="01.01.01.01.001")
        job = JobFactory(project=project)
        group = GroupFactory(name="test group", description="desc", parent=job, depth=1)

        sub_group = GroupFactory(
            name="sub group", description="desc", parent=group, depth=2
        )

        sub_sub_group = GroupFactory(
            name="sub sub group", description="desc", parent=sub_group, depth=3
        )

        serializer = GroupSerializer(instance=group)
        serialized = serializer.data

        self.assertDictContainsSubset(
            {"name": "test group", "description": "desc", "tasks": []}, serialized
        )
        self.assertDictContainsSubset(
            {"name": "sub group", "description": "desc", "tasks": []},
            serialized["groups"][0],
        )
        self.assertDictContainsSubset(
            {"name": "sub sub group", "description": "desc", "tasks": []},
            serialized["groups"][0]["groups"][0],
        )

    def test_can_serialize_group_with_sub_group_with_sub_group_with_tasks(self):
        project = ProjectFactory(structure="01.01.01.01.001")
        job = JobFactory(project=project)
        group = GroupFactory(name="test group", description="desc", parent=job, depth=1)

        sub_group = GroupFactory(
            name="sub group", description="desc", parent=group, depth=2
        )

        sub_sub_group = GroupFactory(
            name="sub sub group", description="desc", parent=sub_group, depth=3
        )

        sub_sub_group_task = TaskFactory(
            name="Cleaning 2",
            group=sub_sub_group,
            qty=1,
            total=1,
            description="clean stuff again",
        )

        serializer = GroupSerializer(instance=group)
        serialized = serializer.data

        self.assertDictContainsSubset(
            {"name": "test group", "description": "desc", "tasks": []}, serialized
        )
        self.assertDictContainsSubset(
            {"name": "sub group", "description": "desc", "tasks": []},
            serialized["groups"][0],
        )
        self.assertDictContainsSubset(
            {"name": "sub sub group", "description": "desc"},
            serialized["groups"][0]["groups"][0],
        )
        self.assertDictContainsSubset(
            {
                "name": "Cleaning 2",
                "qty": 1,
                "total": 1,
                "description": "clean stuff again",
                "lineitems": [],
            },
            serialized["groups"][0]["groups"][0]["tasks"][0],
        )

    def test_can_serialize_group_with_sub_group_with_sub_group_with_tasks_with_lineitems(
        self
    ):
        project = ProjectFactory(structure="01.01.01.01.001")
        job = JobFactory(project=project)
        group = GroupFactory(name="test group", description="desc", parent=job, depth=1)

        sub_group = GroupFactory(
            name="sub group", description="desc", parent=group, depth=2
        )

        sub_sub_group = GroupFactory(
            name="sub sub group", description="desc", parent=sub_group, depth=3
        )

        sub_sub_group_task = TaskFactory(
            name="Cleaning 2",
            group=sub_sub_group,
            qty=1,
            total=1,
            description="clean stuff again",
        )

        LineItemFactory(
            name="Clean celing", unit="hr", qty=8, price=12, task=sub_sub_group_task
        )
        LineItemFactory(
            name="Clean floor", unit="hr", qty=4, price=26, task=sub_sub_group_task
        )
        LineItemFactory(
            name="Clean doors", unit="hr", qty=4, price=20, task=sub_sub_group_task
        )

        serializer = GroupSerializer(instance=group)
        serialized = serializer.data

        self.assertDictContainsSubset(
            {"name": "test group", "description": "desc", "tasks": []}, serialized
        )
        self.assertDictContainsSubset(
            {"name": "sub group", "description": "desc", "tasks": []},
            serialized["groups"][0],
        )
        self.assertDictContainsSubset(
            {"name": "sub sub group", "description": "desc"},
            serialized["groups"][0]["groups"][0],
        )
        self.assertDictContainsSubset(
            {
                "name": "Cleaning 2",
                "qty": 1,
                "total": 1,
                "description": "clean stuff again",
            },
            serialized["groups"][0]["groups"][0]["tasks"][0],
        )
        self.assertDictContainsSubset(
            {"name": "Clean celing", "unit": "hr", "qty": "8.000", "price": "12.00"},
            serialized["groups"][0]["groups"][0]["tasks"][0]["lineitems"][0],
        )
        self.assertDictContainsSubset(
            {"name": "Clean floor", "unit": "hr", "qty": "4.000", "price": "26.00"},
            serialized["groups"][0]["groups"][0]["tasks"][0]["lineitems"][1],
        )
        self.assertDictContainsSubset(
            {"name": "Clean doors", "unit": "hr", "qty": "4.000", "price": "20.00"},
            serialized["groups"][0]["groups"][0]["tasks"][0]["lineitems"][2],
        )
