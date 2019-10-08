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
from systori.apps.task.models import Group, LineItem, Task, Job
from systori.apps.task.serializers import (
    TaskSerializer,
    GroupSerializer,
    LineItemSerializer,
    JobSerializer,
)


class LineItemSerializerTest(ClientTestCase):
    def setUp(self):
        super().setUp()
        # Has structure 01.01.001
        self.project = ProjectFactory()
        self.jobsite = JobSiteFactory(project=self.project)

    def test_can_serialize_no_lineitems(self):
        self.assertEqual(LineItemSerializer(many=True, instance=[]).data, [])

    def test_can_serialize_single_lineitem(self, task=None, task_parent=None):
        """
        task_parent: Either a Job (default) or a Group
        """
        task_parent = task_parent or JobFactory(project=self.project)
        task = task or TaskFactory(
            job=task_parent
            if isinstance(task_parent, (Job, JobFactory))
            else task_parent.job,
            group=task_parent
            if isinstance(task_parent, (Group, GroupFactory))
            else None,
            price=5,
            complete=10,
            total=100,
            description="This is a test task",
        )

        lineitem1 = LineItemFactory(unit="hr", qty=8, price=12, task=task)

        serializer = LineItemSerializer(instance=lineitem1)
        serialized = serializer.data

        self.assertDictEqual(
            {
                "pk": lineitem1.pk,
                "token": None,
                "name": lineitem1.name,
                "order": lineitem1.order,
                "qty": "8.000",
                "qty_equation": "",
                "unit": "hr",
                "price": "12.00",
                "price_equation": "",
                "total": "0.00",
                "total_equation": "",
                "is_hidden": lineitem1.is_hidden,
                "lineitem_type": "other",
            },
            serialized,
        )

        # When this method is used externally
        if not isinstance(self, LineItemSerializerTest):
            return serialized

        for lineitem_type, _ in LineItem.LINEITEM_TYPES:
            lineitem_with_type = LineItemFactory(
                unit="hr", qty=8, price=12, task=task, lineitem_type=lineitem_type
            )
            serializer = LineItemSerializer(instance=lineitem_with_type)
            serialized_with_lineitem_type = serializer.data
            self.assertDictEqual(
                {
                    "pk": lineitem_with_type.pk,
                    "token": None,
                    "name": lineitem_with_type.name,
                    "order": lineitem_with_type.order,
                    "qty": "8.000",
                    "qty_equation": "",
                    "unit": "hr",
                    "price": "12.00",
                    "price_equation": "",
                    "total": "0.00",
                    "total_equation": "",
                    "is_hidden": lineitem_with_type.is_hidden,
                    "lineitem_type": lineitem_type,
                },
                serialized_with_lineitem_type,
                f"Failed for LineItemType: {lineitem_type}",
            )

    def test_can_serialize_multiple_lineitems(self, task=None, task_parent=None):
        """
        task_parent: Either a Job (default) or a Group
        """
        task_parent = task_parent or JobFactory(project=self.project)
        task = task or TaskFactory(
            job=task_parent
            if isinstance(task_parent, (Job, JobFactory))
            else task_parent.job,
            group=task_parent
            if isinstance(task_parent, (Group, GroupFactory))
            else None,
            price=5,
            complete=10,
            total=100,
            description="This is a test task",
        )

        lineitem1 = LineItemFactory(unit="hr", qty=8, price=12, task=task)
        lineitem2 = LineItemFactory(unit="hr", qty=48, price=3, task=task)

        serializer = LineItemSerializer(many=True, instance=[lineitem1, lineitem2])
        serialized = serializer.data
        self.assertEqual(len(serialized), 2)

        self.assertDictEqual(
            {
                "pk": lineitem1.pk,
                "token": None,
                "name": lineitem1.name,
                "order": lineitem1.order,
                "qty": "8.000",
                "qty_equation": "",
                "unit": "hr",
                "price": "12.00",
                "price_equation": "",
                "total": "0.00",
                "total_equation": "",
                "is_hidden": lineitem1.is_hidden,
                "lineitem_type": "other",
            },
            serialized[0],
        )
        self.assertDictEqual(
            {
                "pk": lineitem2.pk,
                "token": None,
                "name": lineitem2.name,
                "order": lineitem2.order,
                "qty": "48.000",
                "qty_equation": "",
                "unit": "hr",
                "price": "3.00",
                "price_equation": "",
                "total": "0.00",
                "total_equation": "",
                "is_hidden": lineitem2.is_hidden,
                "lineitem_type": "other",
            },
            serialized[1],
        )

        # When this method is used externally
        if not isinstance(self, LineItemSerializerTest):
            return serialized


class TaskSerializerTest(ClientTestCase):
    def setUp(self):
        super().setUp()
        # Has structure 01.01.001
        self.project = ProjectFactory()
        self.jobsite = JobSiteFactory(project=self.project)

    # Test cases that can be used externally
    TEST_CASES = (
        "test_can_serialize_single_task_with_no_lineitems",
        "test_can_serialize_single_task_with_multiple_lineitems",
        "test_can_serialize_multiple_tasks_with_no_lineitems",
        "test_can_serialize_multiple_tasks_with_multiple_lineitems",
    )

    def test_can_serialize_no_tasks(self):
        self.assertEqual(TaskSerializer(many=True, instance=[]).data, [])

    def test_can_serialize_single_task_with_no_lineitems(self, parent=None):
        """
        parent: Either a Job (default) or a Group
        """
        parent = parent or JobFactory(project=self.project)
        task = TaskFactory(
            job=parent if isinstance(parent, (Job, JobFactory)) else parent.job,
            group=parent if isinstance(parent, (Group, GroupFactory)) else None,
            price=5,
            complete=10,
            total=100,
            description="This is a test task",
        )

        serializer = TaskSerializer(instance=task)
        serialized = serializer.data

        self.assertDictEqual(
            {
                "pk": task.pk,
                "token": None,
                "name": task.name,
                "description": "This is a test task",
                "order": task.order,
                "qty": "0.000",
                "qty_equation": "",
                "unit": "",
                "price": "5.00",
                "price_equation": "",
                "total": "100.00",
                "total_equation": "",
                "variant_group": task.variant_group,
                "variant_serial": task.variant_serial,
                "is_provisional": task.is_provisional,
                # "status": "",
                "job": (
                    parent.pk
                    if isinstance(parent, (Job, JobFactory))
                    else parent.job.pk
                ),
                "group": (
                    parent.pk if isinstance(parent, (Group, GroupFactory)) else None
                ),
                "lineitems": [],
            },
            serialized,
        )

        # When this method is used externally
        if not isinstance(self, TaskSerializerTest):
            return serialized

        for status, _ in Task.STATE_CHOICES:
            task = TaskFactory(
                job=parent if isinstance(parent, (Job, JobFactory)) else parent.job,
                group=parent if isinstance(parent, (Group, GroupFactory)) else None,
                price=5,
                complete=10,
                total=100,
                status=status,
                description="This is a test task",
            )

            serializer = TaskSerializer(instance=task)
            serialized_with_status = serializer.data
            self.assertDictEqual(
                {
                    "pk": task.pk,
                    "token": None,
                    "name": task.name,
                    "description": "This is a test task",
                    "order": task.order,
                    "qty": "0.000",
                    "qty_equation": "",
                    "unit": "",
                    "price": "5.00",
                    "price_equation": "",
                    "total": "100.00",
                    "total_equation": "",
                    "variant_group": task.variant_group,
                    "variant_serial": task.variant_serial,
                    "is_provisional": task.is_provisional,
                    # "status": status,
                    "job": (
                        parent.pk
                        if isinstance(parent, (Job, JobFactory))
                        else parent.job.pk
                    ),
                    "group": (
                        parent.pk if isinstance(parent, (Group, GroupFactory)) else None
                    ),
                    "lineitems": [],
                },
                serialized_with_status,
                f"Failed for Task status: {status}",
            )

    def test_can_serialize_multiple_tasks_with_no_lineitems(self, parent=None):
        """
        parent: Either a Job (default) or a Group
        """
        parent = parent or JobFactory(project=self.project)
        task1 = TaskFactory(
            job=parent if isinstance(parent, (Job, JobFactory)) else parent.job,
            group=parent if isinstance(parent, (Group, GroupFactory)) else None,
            price=5,
            complete=10,
            total=100,
            description="This is test task1",
        )
        task2 = TaskFactory(
            job=parent if isinstance(parent, (Job, JobFactory)) else parent.job,
            group=parent if isinstance(parent, (Group, GroupFactory)) else None,
            price=25,
            complete=20,
            total=25,
            description="This is test task2",
        )

        serializer = TaskSerializer(many=True, instance=[task1, task2])
        serialized = serializer.data

        self.assertEqual(len(serialized), 2)

        self.assertDictEqual(
            {
                "pk": task1.pk,
                "token": None,
                "name": task1.name,
                "description": "This is test task1",
                "order": task1.order,
                "qty": "0.000",
                "qty_equation": "",
                "unit": "",
                "price": "5.00",
                "price_equation": "",
                "total": "100.00",
                "total_equation": "",
                "variant_group": task1.variant_group,
                "variant_serial": task1.variant_serial,
                "is_provisional": task1.is_provisional,
                # "status": "",
                "job": (
                    parent.pk
                    if isinstance(parent, (Job, JobFactory))
                    else parent.job.pk
                ),
                "group": (
                    parent.pk if isinstance(parent, (Group, GroupFactory)) else None
                ),
                "lineitems": [],
            },
            serialized[0],
        )
        self.assertDictEqual(
            {
                "pk": task2.pk,
                "token": None,
                "name": task2.name,
                "description": "This is test task2",
                "order": task2.order,
                "qty": "0.000",
                "qty_equation": "",
                "unit": "",
                "price": "25.00",
                "price_equation": "",
                "total": "25.00",
                "total_equation": "",
                "variant_group": task2.variant_group,
                "variant_serial": task2.variant_serial,
                "is_provisional": task2.is_provisional,
                # "status": "",
                "job": (
                    parent.pk
                    if isinstance(parent, (Job, JobFactory))
                    else parent.job.pk
                ),
                "group": (
                    parent.pk if isinstance(parent, (Group, GroupFactory)) else None
                ),
                "lineitems": [],
            },
            serialized[1],
        )

        # When this method is used externally
        if not isinstance(self, TaskSerializerTest):
            return serialized

    def test_can_serialize_single_task_with_multiple_lineitems(self, parent=None):
        """
        parent: Either a Job (default) or a Group
        """
        parent = parent or JobFactory(project=self.project)
        task = TaskFactory(
            job=parent if isinstance(parent, (Job, JobFactory)) else parent.job,
            group=parent if isinstance(parent, (Group, GroupFactory)) else None,
            price=5,
            complete=10,
            total=100,
            description="This is a test task",
        )

        #  make sure this task is not causing lineitem serialization to fail
        lineitems = LineItemSerializerTest.test_can_serialize_multiple_lineitems(
            self, task=task
        )

        serializer = TaskSerializer(instance=task)
        serialized = serializer.data

        self.assertDictEqual(
            {
                "pk": task.pk,
                "token": None,
                "name": task.name,
                "description": "This is a test task",
                "order": task.order,
                "qty": "0.000",
                "qty_equation": "",
                "unit": "",
                "price": "5.00",
                "price_equation": "",
                "total": "100.00",
                "total_equation": "",
                "variant_group": task.variant_group,
                "variant_serial": task.variant_serial,
                "is_provisional": task.is_provisional,
                # "status": "",
                "job": (
                    parent.pk
                    if isinstance(parent, (Job, JobFactory))
                    else parent.job.pk
                ),
                "group": (
                    parent.pk if isinstance(parent, (Group, GroupFactory)) else None
                ),
                "lineitems": lineitems,
            },
            serialized,
        )

        # When this method is used externally
        if not isinstance(self, TaskSerializerTest):
            return serialized

    def test_can_serialize_multiple_tasks_with_multiple_lineitems(self, parent=None):
        """
        parent: Either a Job (default) or a Group
        """
        parent = parent or JobFactory(project=self.project)
        task1 = TaskFactory(
            job=parent if isinstance(parent, (Job, JobFactory)) else parent.job,
            group=parent if isinstance(parent, (Group, GroupFactory)) else None,
            price=5,
            complete=10,
            total=100,
            description="This is test task1",
        )
        task2 = TaskFactory(
            job=parent if isinstance(parent, (Job, JobFactory)) else parent.job,
            group=parent if isinstance(parent, (Group, GroupFactory)) else None,
            price=25,
            complete=20,
            total=25,
            description="This is test task2",
        )

        task1_lineitems = LineItemSerializerTest.test_can_serialize_multiple_lineitems(
            self, task=task1
        )
        task2_lineitems = LineItemSerializerTest.test_can_serialize_multiple_lineitems(
            self, task=task2
        )

        serializer = TaskSerializer(many=True, instance=[task1, task2])
        serialized = serializer.data

        self.assertEqual(len(serialized), 2)

        self.assertDictEqual(
            {
                "pk": task1.pk,
                "token": None,
                "name": task1.name,
                "description": "This is test task1",
                "order": task1.order,
                "qty": "0.000",
                "qty_equation": "",
                "unit": "",
                "price": "5.00",
                "price_equation": "",
                "total": "100.00",
                "total_equation": "",
                "variant_group": task1.variant_group,
                "variant_serial": task1.variant_serial,
                "is_provisional": task1.is_provisional,
                # "status": "",
                "job": (
                    parent.pk
                    if isinstance(parent, (Job, JobFactory))
                    else parent.job.pk
                ),
                "group": (
                    parent.pk if isinstance(parent, (Group, GroupFactory)) else None
                ),
                "lineitems": task1_lineitems,
            },
            serialized[0],
        )
        self.assertDictEqual(
            {
                "pk": task2.pk,
                "token": None,
                "name": task2.name,
                "description": "This is test task2",
                "order": task2.order,
                "qty": "0.000",
                "qty_equation": "",
                "unit": "",
                "price": "25.00",
                "price_equation": "",
                "total": "25.00",
                "total_equation": "",
                "variant_group": task2.variant_group,
                "variant_serial": task2.variant_serial,
                "is_provisional": task2.is_provisional,
                # "status": "",
                "job": (
                    parent.pk
                    if isinstance(parent, (Job, JobFactory))
                    else parent.job.pk
                ),
                "group": (
                    parent.pk if isinstance(parent, (Group, GroupFactory)) else None
                ),
                "lineitems": task2_lineitems,
            },
            serialized[1],
        )

        # When this method is used externally
        if not isinstance(self, TaskSerializerTest):
            return serialized

    def test_can_serialize_task_from_from_job(self):
        job = JobFactory(project=self.project)

        self.test_can_serialize_single_task_with_no_lineitems(parent=job)
        self.test_can_serialize_single_task_with_multiple_lineitems(parent=job)

        self.test_can_serialize_single_task_with_multiple_lineitems(parent=job)
        self.test_can_serialize_multiple_tasks_with_multiple_lineitems(parent=job)

    def test_can_serialize_task_from_group_from_job(self):
        job = JobFactory(project=self.project)
        group = GroupFactory(name="test group", description="desc", parent=job, depth=1)

        self.test_can_serialize_single_task_with_no_lineitems(parent=group)
        self.test_can_serialize_single_task_with_multiple_lineitems(parent=group)

        self.test_can_serialize_single_task_with_multiple_lineitems(parent=group)
        self.test_can_serialize_multiple_tasks_with_multiple_lineitems(parent=group)

    def test_can_serialize_task_from_subgroup_from_group_from_job(self):
        project = ProjectFactory(structure="01.01.01.001")
        job = JobFactory(project=project)
        group = GroupFactory(name="test group", description="desc", parent=job, depth=1)
        sub_group = GroupFactory(
            name="test sub group", description="desc", parent=group
        )

        self.test_can_serialize_single_task_with_no_lineitems(parent=sub_group)
        self.test_can_serialize_single_task_with_multiple_lineitems(parent=sub_group)

        self.test_can_serialize_single_task_with_multiple_lineitems(parent=sub_group)
        self.test_can_serialize_multiple_tasks_with_multiple_lineitems(parent=sub_group)


class GroupSerializerTest(ClientTestCase):
    def setUp(self):
        super().setUp()
        # Has structure 01.01.001
        self.project = ProjectFactory()
        self.jobsite = JobSiteFactory(project=self.project)

    def test_can_serialize_no_groups(self):
        self.assertEqual(GroupSerializer(many=True, instance=[]).data, [])

    def test_can_serialize_single_group_with_no_tasks(self, parent=None):
        job = parent or JobFactory(project=self.project)
        group = GroupFactory(name="test group", description="desc", parent=job, depth=1)

        serializer = GroupSerializer(instance=group)
        serialized = serializer.data

        self.assertDictEqual(
            {
                "pk": group.pk,
                "token": group.token,
                "name": "test group",
                "description": "desc",
                "order": group.order,
                "groups": [],
                "tasks": [],
            },
            serialized,
        )

        return group, serialized

    def test_can_serialize_single_group_with_single_task(self, parent=None):

        for task_test in [
            "test_can_serialize_single_task_with_no_lineitems",
            "test_can_serialize_single_task_with_multiple_lineitems",
        ]:

            job = parent or JobFactory(project=self.project)
            group, _ = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
                self, parent=job
            )

            serialized_task = getattr(TaskSerializerTest, task_test)(self, parent=group)

            serializer = GroupSerializer(instance=group)
            serialized = serializer.data

            self.assertDictEqual(
                {
                    "pk": group.pk,
                    "token": group.token,
                    "name": "test group",
                    "description": "desc",
                    "order": group.order,
                    "groups": [],
                    "tasks": [serialized_task],
                },
                serialized,
                f"Failed with single_task_test {task_test}",
            )

    def test_can_serialize_single_group_with_multiple_tasks(self, parent=None):
        for task_test in [
            "test_can_serialize_multiple_tasks_with_no_lineitems",
            "test_can_serialize_multiple_tasks_with_multiple_lineitems",
        ]:

            job = parent or JobFactory(project=self.project)
            group, _ = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
                self, parent=job
            )

            serialized_tasks = getattr(TaskSerializerTest, task_test)(
                self, parent=group
            )

            serializer = GroupSerializer(instance=group)
            serialized = serializer.data

            self.assertDictEqual(
                {
                    "pk": group.pk,
                    "token": group.token,
                    "name": "test group",
                    "description": "desc",
                    "order": group.order,
                    "groups": [],
                    "tasks": serialized_tasks,
                },
                serialized,
                f"Failed with multiple_task_test {task_test}",
            )

    def test_can_serialize_multiple_groups_with_no_tasks(self):
        job = JobFactory(project=self.project)
        group1, _ = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
            self, parent=job
        )
        group2, _ = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
            self, parent=job
        )

        serializer = GroupSerializer(many=True, instance=[group1, group2])
        serialized = serializer.data

        self.assertEqual(len(serialized), 2)

        self.assertDictEqual(
            {
                "pk": group1.pk,
                "token": group1.token,
                "name": "test group",
                "description": "desc",
                "order": group1.order,
                "groups": [],
                "tasks": [],
            },
            serialized[0],
        )
        self.assertDictEqual(
            {
                "pk": group2.pk,
                "token": group2.token,
                "name": "test group",
                "description": "desc",
                "order": group2.order,
                "groups": [],
                "tasks": [],
            },
            serialized[1],
        )

    def test_can_serialize_multiple_groups_with_single_task(self):

        for task_test in [
            "test_can_serialize_single_task_with_no_lineitems",
            "test_can_serialize_single_task_with_multiple_lineitems",
        ]:

            job = JobFactory(project=self.project)
            group1, _ = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
                self, parent=job
            )
            group2, _ = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
                self, parent=job
            )

            serialized_group1_task = getattr(TaskSerializerTest, task_test)(
                self, parent=group1
            )
            serialized_group2_task = getattr(TaskSerializerTest, task_test)(
                self, parent=group2
            )
            serializer = GroupSerializer(many=True, instance=[group1, group2])
            serialized = serializer.data

            self.assertEqual(len(serialized), 2)

            self.assertDictEqual(
                {
                    "pk": group1.pk,
                    "token": group1.token,
                    "name": "test group",
                    "description": "desc",
                    "order": group1.order,
                    "groups": [],
                    "tasks": [serialized_group1_task],
                },
                serialized[0],
            )
            self.assertDictEqual(
                {
                    "pk": group2.pk,
                    "token": group2.token,
                    "name": "test group",
                    "description": "desc",
                    "order": group2.order,
                    "groups": [],
                    "tasks": [serialized_group2_task],
                },
                serialized[1],
            )

    def test_can_serialize_multiple_groups_with_multiple_tasks(self):

        for task_test in [
            "test_can_serialize_multiple_tasks_with_no_lineitems",
            "test_can_serialize_multiple_tasks_with_multiple_lineitems",
        ]:

            job = JobFactory(project=self.project)
            group1, _ = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
                self, parent=job
            )
            group2, _ = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
                self, parent=job
            )

            serialized_group1_tasks = getattr(TaskSerializerTest, task_test)(
                self, parent=group1
            )
            serialized_group2_tasks = getattr(TaskSerializerTest, task_test)(
                self, parent=group2
            )
            serializer = GroupSerializer(many=True, instance=[group1, group2])
            serialized = serializer.data

            self.assertEqual(len(serialized), 2)

            self.assertDictEqual(
                {
                    "pk": group1.pk,
                    "token": group1.token,
                    "name": "test group",
                    "description": "desc",
                    "order": group1.order,
                    "groups": [],
                    "tasks": serialized_group1_tasks,
                },
                serialized[0],
            )
            self.assertDictEqual(
                {
                    "pk": group2.pk,
                    "token": group2.token,
                    "name": "test group",
                    "description": "desc",
                    "order": group2.order,
                    "groups": [],
                    "tasks": serialized_group2_tasks,
                },
                serialized[1],
            )

    def test_can_serialize_single_subgroup_with_no_tasks(self):
        project = ProjectFactory(structure="01.01.01.001")
        job = JobFactory(project=project)
        group, _ = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
            self, parent=job
        )

        sub_group, _ = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
            self, parent=group
        )

        serialized_group = GroupSerializer(instance=group).data
        serialized_subgroup = GroupSerializer(instance=sub_group).data

        self.assertDictEqual(
            {
                "pk": group.pk,
                "token": group.token,
                "name": "test group",
                "description": "desc",
                "order": group.order,
                "groups": [serialized_subgroup],
                "tasks": [],
            },
            serialized_group,
        )

    def test_can_serialize_single_subgroup_with_single_task(self):
        for task_test in [
            "test_can_serialize_single_task_with_no_lineitems",
            "test_can_serialize_single_task_with_multiple_lineitems",
        ]:

            project = ProjectFactory(structure="01.01.01.001")
            job = JobFactory(project=project)
            group, _ = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
                self, parent=job
            )

            sub_group, _ = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
                self, parent=group
            )

            serialized_task = getattr(TaskSerializerTest, task_test)(
                self, parent=sub_group
            )

            serialized_group = GroupSerializer(instance=group).data
            serialized_subgroup = GroupSerializer(instance=sub_group).data

            self.assertDictEqual(
                {
                    "pk": group.pk,
                    "token": group.token,
                    "name": "test group",
                    "description": "desc",
                    "order": group.order,
                    "groups": [
                        {
                            "pk": sub_group.pk,
                            "token": sub_group.token,
                            "name": "test group",
                            "description": "desc",
                            "order": sub_group.order,
                            "groups": [],
                            "tasks": [serialized_task],
                        }
                    ],
                    "tasks": [],
                },
                serialized_group,
                f"Failed with single_task_test: {task_test}",
            )

    def test_can_serialize_single_subgroup_with_multiple_tasks(self):
        for task_test in [
            "test_can_serialize_multiple_tasks_with_no_lineitems",
            "test_can_serialize_multiple_tasks_with_multiple_lineitems",
        ]:

            project = ProjectFactory(structure="01.01.01.001")
            job = JobFactory(project=project)
            group, _ = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
                self, parent=job
            )

            sub_group, _ = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
                self, parent=group
            )

            serialized_tasks = getattr(TaskSerializerTest, task_test)(
                self, parent=sub_group
            )

            serialized_group = GroupSerializer(instance=group).data

            self.assertDictEqual(
                {
                    "pk": group.pk,
                    "token": group.token,
                    "name": "test group",
                    "description": "desc",
                    "order": group.order,
                    "groups": [
                        {
                            "pk": sub_group.pk,
                            "token": sub_group.token,
                            "name": "test group",
                            "description": "desc",
                            "order": sub_group.order,
                            "groups": [],
                            "tasks": serialized_tasks,
                        }
                    ],
                    "tasks": [],
                },
                serialized_group,
                f"Failed with single_task_test: {task_test}",
            )

    def test_can_serialize_multiple_subgroup_with_no_tasks(self):
        project = ProjectFactory(structure="01.01.01.001")
        job = JobFactory(project=project)
        group, _ = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
            self, parent=job
        )

        sub_group1, _ = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
            self, parent=group
        )
        sub_group2, _ = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
            self, parent=group
        )

        serialized_group = GroupSerializer(instance=group).data
        serialized_subgroup1 = GroupSerializer(instance=sub_group1).data
        serialized_subgroup2 = GroupSerializer(instance=sub_group2).data

        self.assertDictEqual(
            {
                "pk": group.pk,
                "token": group.token,
                "name": "test group",
                "description": "desc",
                "order": group.order,
                "groups": [serialized_subgroup1, serialized_subgroup2],
                "tasks": [],
            },
            serialized_group,
        )

    def test_can_serialize_multiple_subgroup_with_single_task(self):
        for task_test in [
            "test_can_serialize_single_task_with_no_lineitems",
            "test_can_serialize_single_task_with_multiple_lineitems",
        ]:

            project = ProjectFactory(structure="01.01.01.001")
            job = JobFactory(project=project)
            group, _ = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
                self, parent=job
            )

            sub_group1, _ = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
                self, parent=group
            )
            sub_group2, _ = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
                self, parent=group
            )

            serialized_subgroup1_task = getattr(TaskSerializerTest, task_test)(
                self, parent=sub_group1
            )
            serialized_subgroup2_task = getattr(TaskSerializerTest, task_test)(
                self, parent=sub_group2
            )

            serialized_group = GroupSerializer(instance=group).data

            self.assertDictEqual(
                {
                    "pk": group.pk,
                    "token": group.token,
                    "name": "test group",
                    "description": "desc",
                    "order": group.order,
                    "groups": [
                        {
                            "pk": sub_group1.pk,
                            "token": sub_group1.token,
                            "name": "test group",
                            "description": "desc",
                            "order": sub_group1.order,
                            "groups": [],
                            "tasks": [serialized_subgroup1_task],
                        },
                        {
                            "pk": sub_group2.pk,
                            "token": sub_group2.token,
                            "name": "test group",
                            "description": "desc",
                            "order": sub_group2.order,
                            "groups": [],
                            "tasks": [serialized_subgroup2_task],
                        },
                    ],
                    "tasks": [],
                },
                serialized_group,
                f"Failed with single_task_test: {task_test}",
            )

    def test_can_serialize_multiple_subgroup_with_multiple_tasks(self):
        for task_test in [
            "test_can_serialize_multiple_tasks_with_no_lineitems",
            "test_can_serialize_multiple_tasks_with_multiple_lineitems",
        ]:

            project = ProjectFactory(structure="01.01.01.001")
            job = JobFactory(project=project)
            group, _ = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
                self, parent=job
            )

            sub_group1, _ = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
                self, parent=group
            )
            sub_group2, _ = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
                self, parent=group
            )

            serialized_subgroup1_tasks = getattr(TaskSerializerTest, task_test)(
                self, parent=sub_group1
            )
            serialized_subgroup2_tasks = getattr(TaskSerializerTest, task_test)(
                self, parent=sub_group2
            )

            serialized_group = GroupSerializer(instance=group).data

            self.assertDictEqual(
                {
                    "pk": group.pk,
                    "token": group.token,
                    "name": "test group",
                    "description": "desc",
                    "order": group.order,
                    "groups": [
                        {
                            "pk": sub_group1.pk,
                            "token": sub_group1.token,
                            "name": "test group",
                            "description": "desc",
                            "order": sub_group1.order,
                            "groups": [],
                            "tasks": serialized_subgroup1_tasks,
                        },
                        {
                            "pk": sub_group2.pk,
                            "token": sub_group2.token,
                            "name": "test group",
                            "description": "desc",
                            "order": sub_group2.order,
                            "groups": [],
                            "tasks": serialized_subgroup2_tasks,
                        },
                    ],
                    "tasks": [],
                },
                serialized_group,
                f"Failed with single_task_test: {task_test}",
            )


class JobSerializerTest(ClientTestCase):
    def setUp(self):
        super().setUp()
        # Has structure 01.01.001
        self.project = ProjectFactory()
        self.jobsite = JobSiteFactory(project=self.project)

    def test_can_serialize_no_jobs(self):
        self.assertEqual(JobSerializer(many=True, instance=[]).data, [])

    def test_can_serialize_single_job_with_no_tasks_no_groups(self):
        job = JobFactory(project=self.project)

        serialized = JobSerializer(instance=job).data

        self.assertDictEqual(
            {
                "pk": job.id,
                "name": job.name,
                "description": job.description,
                "groups": [],
                "tasks": [],
                "order": job.order,
                "delete": {},
            },
            serialized,
        )

    def test_can_serialize_multiple_jobs_with_no_tasks_no_groups(self):
        job1 = JobFactory(project=self.project)
        job2 = JobFactory(project=self.project)

        serialized = JobSerializer(many=True, instance=[job1, job2]).data

        self.assertEqual(len(serialized), 2)

        self.assertDictEqual(
            {
                "pk": job1.id,
                "name": job1.name,
                "description": job1.description,
                "groups": [],
                "tasks": [],
                "order": job1.order,
                "delete": {},
            },
            serialized[0],
        )
        self.assertDictEqual(
            {
                "pk": job2.id,
                "name": job2.name,
                "description": job2.description,
                "groups": [],
                "tasks": [],
                "order": job2.order,
                "delete": {},
            },
            serialized[1],
        )

    def test_can_serialize_single_job_with_single_task_no_groups(self):

        for task_test in [
            "test_can_serialize_single_task_with_no_lineitems",
            "test_can_serialize_single_task_with_multiple_lineitems",
        ]:

            job = JobFactory(project=self.project)

            serialized_task = getattr(TaskSerializerTest, task_test)(self, parent=job)

            serializer = JobSerializer(instance=job)
            serialized = serializer.data
            self.assertDictEqual(
                {
                    "pk": job.id,
                    "name": job.name,
                    "description": job.description,
                    "groups": [],
                    "tasks": [serialized_task],
                    "order": job.order,
                    "delete": {},
                },
                serialized,
                f"Failed with single_task_test {task_test}",
            )

    def test_can_serialize_multiple_jobs_with_single_task_no_groups(self):

        for task_test in [
            "test_can_serialize_single_task_with_no_lineitems",
            "test_can_serialize_single_task_with_multiple_lineitems",
        ]:

            job1 = JobFactory(project=self.project)
            job2 = JobFactory(project=self.project)

            serialized_job1_task = getattr(TaskSerializerTest, task_test)(
                self, parent=job1
            )
            serialized_job2_task = getattr(TaskSerializerTest, task_test)(
                self, parent=job2
            )

            serializer = JobSerializer(many=True, instance=[job1, job2])
            serialized = serializer.data
            self.assertEqual(len(serialized), 2)
            self.assertDictEqual(
                {
                    "pk": job1.id,
                    "name": job1.name,
                    "description": job1.description,
                    "groups": [],
                    "tasks": [serialized_job1_task],
                    "order": job1.order,
                    "delete": {},
                },
                serialized[0],
                f"Failed with single_task_test {task_test}",
            )
            self.assertDictEqual(
                {
                    "pk": job2.id,
                    "name": job2.name,
                    "description": job2.description,
                    "groups": [],
                    "tasks": [serialized_job2_task],
                    "order": job2.order,
                    "delete": {},
                },
                serialized[1],
                f"Failed with single_task_test {task_test}",
            )

    def test_can_serialize_single_job_with_multiple_tasks_no_groups(self):

        for task_test in [
            "test_can_serialize_multiple_tasks_with_no_lineitems",
            "test_can_serialize_multiple_tasks_with_multiple_lineitems",
        ]:

            job = JobFactory(project=self.project)

            serialized_tasks = getattr(TaskSerializerTest, task_test)(self, parent=job)

            serializer = JobSerializer(instance=job)
            serialized = serializer.data
            self.assertDictEqual(
                {
                    "pk": job.id,
                    "name": job.name,
                    "description": job.description,
                    "groups": [],
                    "tasks": serialized_tasks,
                    "order": job.order,
                    "delete": {},
                },
                serialized,
                f"Failed with single_task_test {task_test}",
            )

    def test_can_serialize_multiple_jobs_with_multiple_tasks_no_groups(self):

        for task_test in [
            "test_can_serialize_multiple_tasks_with_no_lineitems",
            "test_can_serialize_multiple_tasks_with_multiple_lineitems",
        ]:

            job1 = JobFactory(project=self.project)
            job2 = JobFactory(project=self.project)

            serialized_job1_tasks = getattr(TaskSerializerTest, task_test)(
                self, parent=job1
            )
            serialized_job2_tasks = getattr(TaskSerializerTest, task_test)(
                self, parent=job2
            )

            serializer = JobSerializer(many=True, instance=[job1, job2])
            serialized = serializer.data
            self.assertEqual(len(serialized), 2)
            self.assertDictEqual(
                {
                    "pk": job1.id,
                    "name": job1.name,
                    "description": job1.description,
                    "groups": [],
                    "tasks": serialized_job1_tasks,
                    "order": job1.order,
                    "delete": {},
                },
                serialized[0],
                f"Failed with single_task_test {task_test}",
            )
            self.assertDictEqual(
                {
                    "pk": job2.id,
                    "name": job2.name,
                    "description": job2.description,
                    "groups": [],
                    "tasks": serialized_job2_tasks,
                    "order": job2.order,
                    "delete": {},
                },
                serialized[1],
                f"Failed with single_task_test {task_test}",
            )

    def test_can_serialize_single_job_with_single_group(self):
        # No tasks
        job = JobFactory(project=self.project)
        group, serialized_group = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
            self, parent=job
        )
        serialized = JobSerializer(instance=job).data

        self.assertDictEqual(
            {
                "pk": job.id,
                "name": job.name,
                "description": job.description,
                "groups": [serialized_group],
                "tasks": [],
                "order": job.order,
                "delete": {},
            },
            serialized,
        )

        # Single task
        for task_test in [
            "test_can_serialize_single_task_with_no_lineitems",
            "test_can_serialize_single_task_with_multiple_lineitems",
        ]:
            job = JobFactory(project=self.project)
            group, _ = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
                self, parent=job
            )
            serialized_task = getattr(TaskSerializerTest, task_test)(self, parent=group)

            serialized = JobSerializer(instance=job).data

            self.assertDictEqual(
                {
                    "pk": job.id,
                    "name": job.name,
                    "description": job.description,
                    "groups": [
                        {
                            "pk": group.pk,
                            "token": group.token,
                            "name": "test group",
                            "description": "desc",
                            "order": group.order,
                            "groups": [],
                            "tasks": [serialized_task],
                        }
                    ],
                    "tasks": [],
                    "order": job.order,
                    "delete": {},
                },
                serialized,
                f"Failed with single_task_test {task_test}",
            )

        # Multiple tasks
        for task_test in [
            "test_can_serialize_multiple_tasks_with_no_lineitems",
            "test_can_serialize_multiple_tasks_with_multiple_lineitems",
        ]:

            job = JobFactory(project=self.project)
            group, _ = GroupSerializerTest.test_can_serialize_single_group_with_no_tasks(
                self, parent=job
            )

            serialized_tasks = getattr(TaskSerializerTest, task_test)(
                self, parent=group
            )

            serializer = JobSerializer(instance=job)
            serialized = serializer.data

            self.assertDictEqual(
                {
                    "pk": job.id,
                    "name": job.name,
                    "description": job.description,
                    "groups": [
                        {
                            "pk": group.pk,
                            "token": group.token,
                            "name": "test group",
                            "description": "desc",
                            "order": group.order,
                            "groups": [],
                            "tasks": serialized_tasks,
                        }
                    ],
                    "tasks": [],
                    "order": job.order,
                    "delete": {},
                },
                serialized,
                f"Failed with multiple_task_test {task_test}",
            )
