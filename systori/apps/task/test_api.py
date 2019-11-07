from decimal import Decimal

from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

import systori.apps.task.flutter_serializers as flutter
from systori.apps.project.factories import JobSiteFactory, ProjectFactory
from systori.apps.task.factories import (
    GroupFactory,
    JobFactory,
    LineItemFactory,
    TaskFactory,
)
from systori.apps.task.models import Group, LineItem, Task
from systori.lib.testing import ClientTestCase


class EditorApiTest(ClientTestCase):
    def test_create_group(self):
        job = JobFactory(project=ProjectFactory())
        response = self.client.post(
            reverse("api.editor.save", args=(job.pk,)),
            {
                "groups": [
                    {
                        "token": 9006199254740991,
                        "name": "test group",
                        "order": 5,
                        "groups": [
                            {
                                "token": 9006199254740992,
                                "name": "sub group",
                                "order": 7,
                            },
                            {
                                "token": 9006199254740993,
                                "name": "sub group 2",
                                "order": 8,
                                "groups": [
                                    {
                                        "token": 9006199254740994,
                                        "name": "sub sub group",
                                        "order": 1,
                                    }
                                ],
                            },
                        ],
                    }
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(5, Group.objects.count())
        group = Group.objects.get(parent=job)
        self.assertEqual("test group", group.name)
        self.assertEqual(5, group.order)
        self.assertEqual("sub group", group.groups.all()[0].name)
        self.assertEqual("sub group 2", group.groups.all()[1].name)
        self.assertEqual(8, group.groups.all()[1].order)
        self.assertEqual("sub sub group", group.groups.all()[1].groups.all()[0].name)
        self.maxDiff = None
        self.assertDictEqual(
            {
                "token": None,
                "pk": 1,
                "groups": [
                    {
                        "token": 9006199254740991,
                        "pk": 2,
                        "groups": [
                            {"token": 9006199254740992, "pk": 3},
                            {
                                "token": 9006199254740993,
                                "pk": 4,
                                "groups": [{"token": 9006199254740994, "pk": 5}],
                            },
                        ],
                    }
                ],
            },
            response.data,
        )

    def test_create_group_idempotent(self):
        job = JobFactory(project=ProjectFactory())

        response = self.client.post(
            reverse("api.editor.save", args=(job.pk,)),
            {
                "groups": [
                    {
                        "token": 7,
                        "name": "test group",
                        "groups": [{"token": 8, "name": "sub group"}],
                    }
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(3, Group.objects.count())
        self.assertDictEqual(
            {
                "token": None,
                "pk": 1,
                "groups": [{"token": 7, "pk": 2, "groups": [{"token": 8, "pk": 3}]}],
            },
            response.data,
        )

        response = self.client.post(
            reverse("api.editor.save", args=(job.pk,)),
            {
                "groups": [
                    {
                        "token": 7,
                        "name": "test group",
                        "groups": [{"token": 8, "name": "sub group"}],
                    }
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(3, Group.objects.count())
        self.assertDictEqual(
            {
                "token": None,
                "pk": 1,
                "groups": [{"token": 7, "pk": 2, "groups": [{"token": 8, "pk": 3}]}],
            },
            response.data,
        )

    def test_update_group(self):
        job = JobFactory(project=ProjectFactory())
        group1 = GroupFactory(name="group 1 for update", parent=job)
        group2 = GroupFactory(name="group 2 for update", parent=job)
        self.assertEqual(3, Group.objects.count())
        self.assertSequenceEqual(
            job.groups.values_list("name", flat=True), [group1.name, group2.name]
        )

        response = self.client.post(
            reverse("api.editor.save", args=(job.pk,)),
            {
                "groups": [
                    {"pk": group1.pk, "name": "updated group", "order": 2},
                    {"pk": group2.pk, "order": 1},
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertSequenceEqual(
            job.groups.values_list("name", flat=True), [group2.name, "updated group"]
        )

        group1.refresh_from_db()
        self.assertEqual(3, Group.objects.count())
        self.assertEqual("updated group", group1.name)
        self.assertDictEqual(
            {
                "token": None,
                "pk": 1,
                "groups": [
                    {"token": None, "pk": group1.pk},
                    {"token": None, "pk": group2.pk},
                ],
            },
            response.data,
        )

    def test_delete_group(self):
        project = ProjectFactory(structure="0.0.0.0")
        job = JobFactory(project=project, generate_groups=True)
        self.assertEqual(3, Group.objects.count())
        response = self.client.post(
            reverse("api.editor.save", args=(job.pk,)),
            {"delete": {"groups": [2]}},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(1, Group.objects.count())

    def test_create_task_idempotent(self):
        job = JobFactory(project=ProjectFactory())
        response = self.client.post(
            reverse("api.editor.save", args=(job.pk,)),
            {
                "tasks": [
                    {
                        "token": 9006199254740991,
                        "name": "test task",
                        "description": "",
                        "qty_equation": "",
                        "unit": "",
                        "price_equation": "",
                        "total_equation": "",
                        "lineitems": [
                            {
                                "token": 9006199254740992,
                                "name": "lineitem",
                                "qty_equation": "",
                                "unit": "",
                                "price_equation": "",
                                "total_equation": "",
                            },
                            {
                                "token": 9006199254740993,
                                "name": "lineitem 2",
                                "qty_equation": "",
                                "unit": "",
                                "price_equation": "",
                                "total_equation": "",
                            },
                        ],
                    }
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(1, Group.objects.count())
        self.assertEqual(1, Task.objects.count())
        self.assertEqual(2, LineItem.objects.count())
        task = job.tasks.all()[0]
        self.assertEqual("test task", task.name)
        self.assertEqual("lineitem", task.lineitems.all()[0].name)
        self.assertEqual("lineitem 2", task.lineitems.all()[1].name)
        self.assertDictEqual(
            {
                "pk": 1,
                "token": None,
                "tasks": [
                    {
                        "pk": 1,
                        "token": 9006199254740991,
                        "lineitems": [
                            {"token": 9006199254740992, "pk": 1},
                            {"token": 9006199254740993, "pk": 2},
                        ],
                    }
                ],
            },
            response.data,
        )

        response = self.client.post(
            reverse("api.editor.save", args=(job.pk,)),
            {
                "tasks": [
                    {
                        "token": 9006199254740991,
                        "name": "test task",
                        "description": "",
                        "qty_equation": "",
                        "unit": "",
                        "price_equation": "",
                        "total_equation": "",
                        "lineitems": [
                            {
                                "token": 9006199254740992,
                                "name": "lineitem",
                                "qty_equation": "",
                                "unit": "",
                                "price_equation": "",
                                "total_equation": "",
                            },
                            {
                                "token": 9006199254740993,
                                "name": "lineitem 2",
                                "qty_equation": "",
                                "unit": "",
                                "price_equation": "",
                                "total_equation": "",
                            },
                        ],
                    }
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(1, Group.objects.count())
        self.assertEqual(1, Task.objects.count())
        self.assertEqual(2, LineItem.objects.count())
        task = job.tasks.all()[0]
        self.assertEqual("test task", task.name)
        self.assertEqual("lineitem", task.lineitems.all()[0].name)
        self.assertEqual("lineitem 2", task.lineitems.all()[1].name)
        self.assertDictEqual(
            {
                "pk": 1,
                "token": None,
                "tasks": [
                    {
                        "pk": 1,
                        "token": 9006199254740991,
                        "lineitems": [
                            {"token": 9006199254740992, "pk": 1},
                            {"token": 9006199254740993, "pk": 2},
                        ],
                    }
                ],
            },
            response.data,
        )

    def test_delete_task(self):
        job = JobFactory(project=ProjectFactory(structure="0.0.0.0"))
        TaskFactory(group=job)
        TaskFactory(group=job)
        self.assertEqual(2, Task.objects.count())
        response = self.client.post(
            reverse("api.editor.save", args=(job.pk,)),
            {"delete": {"tasks": [1]}},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(1, Task.objects.count())

    def test_update_task(self):
        job = JobFactory(project=ProjectFactory())
        task = TaskFactory(group=job)
        lineitem = LineItemFactory(task=task)
        response = self.client.post(
            reverse("api.editor.save", args=(job.pk,)),
            {
                "tasks": [
                    {
                        "pk": task.pk,
                        "total": 11,
                        "lineitems": [{"pk": lineitem.pk, "total": 22}],
                    }
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        task = job.tasks.all()[0]
        self.assertEqual(11, task.total)
        self.assertEqual(22, task.lineitems.all()[0].total)
        self.assertDictEqual(
            {
                "pk": 1,
                "token": None,
                "tasks": [
                    {"pk": 1, "token": None, "lineitems": [{"pk": 1, "token": None}]}
                ],
            },
            response.data,
        )

    def test_delete_lineitem(self):
        job = JobFactory(project=ProjectFactory())
        task = TaskFactory(group=job)
        LineItemFactory(task=task)
        LineItemFactory(task=task)
        self.assertEqual(2, LineItem.objects.count())
        response = self.client.post(
            reverse("api.editor.save", args=(job.pk,)),
            {"delete": {"lineitems": [1]}},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(1, LineItem.objects.count())


class AutocompleteApiTest(ClientTestCase):
    def test_group_completion(self):
        job = JobFactory(
            name="The Job",
            project=ProjectFactory(structure="01.01.001"),
            generate_groups=True,
        )
        GroupFactory(parent=job, name="Voranstrich aus Bitumenlösung")
        GroupFactory(parent=job, name="Schächte und Fundamente")
        response = self.client.post(
            reverse("api.editor.search"),
            {"model_type": "group", "remaining_depth": 0, "terms": "bitumenlos"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(
            response.data,
            [
                {
                    "id": 3,
                    "job__name": "The Job",
                    "match_name": "Voranstrich aus <b>Bitumenlösung</b>",
                    "match_description": "",
                    "rank": 0.607927,
                }
            ],
        )

    def test_group_info(self):
        self.user.language = "de"
        self.user.save()
        job = JobFactory(name="The Job", project=ProjectFactory(structure="01.001"))
        group = GroupFactory(parent=job, name="Voranstrich aus Bitumenlösung")
        TaskFactory(group=group, total=59.97)
        response = self.client.get(
            reverse("api.editor.info", args=["group", group.pk]), format="json"
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertDictEqual(
            response.data,
            {
                "name": "Voranstrich aus Bitumenlösung",
                "description": "",
                "total": "59,97",
            },
        )

    def test_task_completion(self):
        job = JobFactory(name="The Job", project=ProjectFactory(structure="01.001"))
        TaskFactory(
            group=job,
            name="Voranstrich aus Bitumenlösung",
            qty=3,
            unit="m",
            price=19.99,
            total=59.97,
        )
        TaskFactory(group=job, name="Schächte und Fundamente")
        response = self.client.post(
            reverse("api.editor.search"),
            {"model_type": "task", "terms": "bitumenlos"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(
            response.data,
            [
                {
                    "id": 1,
                    "match_name": "Voranstrich aus <b>Bitumenlösung</b>",
                    "match_description": "",
                }
            ],
        )

    def test_task_info(self):
        self.user.language = "de"
        self.user.save()
        job = JobFactory(name="The Job", project=ProjectFactory(structure="01.001"))
        task = TaskFactory(
            group=job,
            name="Voranstrich aus Bitumenlösung",
            qty=3,
            unit="m",
            price=19.99,
            total=59.97,
        )
        LineItemFactory(
            task=task, name="The Line Item", qty=1, unit="h", price=19.99, total=19.99
        )
        response = self.client.get(
            reverse("api.editor.info", args=["task", task.pk]), format="json"
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.maxDiff = None
        self.assertDictEqual(
            response.data,
            {
                "name": "Voranstrich aus Bitumenlösung",
                "description": "",
                "project_id": 2,
                "project_string": "Projekt",
                "qty": "3",
                "unit": "m",
                "price": "19,99",
                "total": "59,97",
                "lineitems": [
                    {
                        "name": "The Line Item",
                        "qty": "1",
                        "unit": "h",
                        "price": "19,99",
                        "total": "19,99",
                    }
                ],
            },
        )

    def test_group_clone(self):
        job = JobFactory(project=ProjectFactory(structure="01.01.001"))
        group = GroupFactory(parent=job, name="Groupy Group")
        job2 = JobFactory(project=ProjectFactory(structure="01.01.001"))
        self.assertEqual(job2.groups.count(), 0)
        response = self.client.post(
            reverse("api.editor.clone"),
            {
                "source_type": "group",
                "source_pk": group.pk,
                "target_pk": job2.pk,
                "position": 1,
            },
            format="json",
        )
        self.assertEqual(job2.groups.first().name, "Groupy Group")
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(len(response.data), 1)

    def test_task_clone(self):
        job = JobFactory(project=ProjectFactory(structure="01.01.001"))
        group = GroupFactory(parent=job, name="Groupy Group")
        task = TaskFactory(group=group, name="Easy Task")
        job2 = JobFactory(project=ProjectFactory(structure="01.001"))
        self.assertEqual(job2.tasks.count(), 0)
        response = self.client.post(
            reverse("api.editor.clone"),
            {
                "source_type": "task",
                "source_pk": task.pk,
                "target_pk": job2.pk,
                "position": 1,
            },
            format="json",
        )
        self.assertEqual(job2.tasks.first().name, "Easy Task")
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(len(response.data), 1)


class TaskApiTest(ClientTestCase):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.jobsite = JobSiteFactory(project=self.project)
        self.job = JobFactory(project=self.project, name="this is a test job")
        self.task = TaskFactory(group=self.job)

    def test_task_clone(self):
        job = JobFactory(project=ProjectFactory(structure="01.01.001"))
        group = GroupFactory(parent=job, name="Groupy Group")
        task = TaskFactory(group=group, name="Easy Task")
        job2 = JobFactory(project=ProjectFactory(structure="01.001"))
        self.assertEqual(job2.tasks.count(), 0)
        response = self.client.post(
            "/api/task/task/clone/",
            {"source": task.pk, "target": job2.pk, "position": 1},
            format="json",
        )
        self.assertEqual(job2.tasks.first().name, "Easy Task")
        self.assertEqual(response.status_code, 200, response.data)
        json = response.json()
        self.assertEqual(
            json,
            {
                "pk": job2.tasks.first().pk,
                "name": "Easy Task",
                "description": "",
                "order": 1,
                "qty": "0.000",
                "qty_equation": "",
                "unit": "",
                "price": "0.00",
                "price_equation": "",
                "total": "0.00",
                "total_equation": "",
                "variant_group": 0,
                "variant_serial": 0,
                "is_provisional": False,
                "parent": job2.pk,
                "lineitems": [],
            },
            json,
        )

    def test_search_tasks(self):
        job = JobFactory(name="The Job", project=ProjectFactory(structure="01.001"))
        task1 = TaskFactory(
            group=job,
            name="Voranstrich aus Bitumenlösung",
            qty=3,
            unit="m",
            price=19.99,
            total=59.97,
        )

        task2 = TaskFactory(group=job, name="Schächte und Fundamente")

        response = self.client.post(
            "/api/task/task/search/", {"terms": "bitumenlos"}, format="json"
        )

        self.assertEqual(response.status_code, HTTP_200_OK)

        json = response.json()
        self.assertListEqual(
            json,
            [
                {
                    "pk": 2,
                    "name": "Voranstrich aus Bitumenlösung",
                    "description": "",
                    "total": "59.97",
                    "lineitems": 0,
                }
            ],
            json,
        )

    def test_list_lineitems(self):
        lineitem1 = LineItemFactory(
            task=self.task, name="lineitem 1", qty=1, unit="h", price=19.99, total=19.99
        )

        lineitem2 = LineItemFactory(
            task=self.task,
            name="lineitem 2",
            qty=1,
            unit="pc",
            price=19.99,
            total=19.99,
        )

        response = self.client.get(f"/api/task/task/{self.task.pk}/lineitems/")
        self.assertEqual(response.status_code, HTTP_200_OK)
        json = response.json()
        self.assertDictEqual(
            json[0],
            {
                "pk": lineitem1.pk,
                "name": "lineitem 1",
                "order": 1,
                "token": None,
                "qty": "1.000",
                "qty_equation": "",
                "unit": "h",
                "price": "19.99",
                "price_equation": "",
                "total": "19.99",
                "total_equation": "",
                "is_hidden": False,
                "lineitem_type": "other",
            },
        )
        self.assertDictEqual(
            json[1],
            {
                "pk": lineitem2.pk,
                "name": "lineitem 2",
                "order": 2,
                "token": None,
                "qty": "1.000",
                "qty_equation": "",
                "unit": "pc",
                "price": "19.99",
                "price_equation": "",
                "total": "19.99",
                "total_equation": "",
                "is_hidden": False,
                "lineitem_type": "other",
            },
        )

    def test_get_lineitem(self):
        lineitem1 = LineItemFactory(
            task=self.task, name="lineitem 1", qty=1, unit="h", price=19.99, total=19.99
        )

        response = self.client.get(
            f"/api/task/task/{self.task.pk}/lineitem/{lineitem1.pk}/"
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        json = response.json()
        self.assertDictEqual(
            json,
            {
                "pk": lineitem1.pk,
                "name": "lineitem 1",
                "order": 1,
                "token": None,
                "qty": "1.000",
                "qty_equation": "",
                "unit": "h",
                "price": "19.99",
                "price_equation": "",
                "total": "19.99",
                "total_equation": "",
                "is_hidden": False,
                "lineitem_type": "other",
            },
        )

    def test_reject_create_task_with_duplicate_lineitem_token(self):
        self.assertEqual(Task.objects.count(), 0, "Expected zero pre-existing tasks")
        response = self.client.post(
            f"/api/task/job/{self.job.pk}/tasks/",
            {
                "name": "task 1",
                "order": 6,
                "qty": "5.000",
                "unit": "h",
                "price": "50.00",
                "total": "250.00",
                "lineitems": [
                    {
                        "name": "lineitem 1",
                        "order": 1,
                        "token": 1,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    },
                    {
                        "name": "lineitem 2",
                        "order": 2,
                        "token": 1,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    },
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        json = response.json()
        self.assertDictEqual(
            json, {"lineitems": ["Multiple lineitems have same token"]}, json
        )
        self.assertEqual(Task.objects.count(), 0, "Expected no tasks to be created")

    def test_reject_update_task_with_duplicate_lineitem_pk(self):
        self.assertEqual(Task.objects.count(), 1, "Expected 1 pre-existing tasks")
        self.assertEqual(
            LineItem.objects.count(), 0, "Expected zero pre-existing lineitems"
        )
        response = self.client.patch(
            f"/api/task/job/{self.job.pk}/task/{self.task.pk}/",
            {
                "name": "task 1",
                "order": 6,
                "qty": "5.000",
                "unit": "h",
                "price": "50.00",
                "total": "250.00",
                "lineitems": [
                    {
                        "name": "lineitem 1",
                        "order": 1,
                        "pk": 1,
                        "token": 1,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    },
                    {
                        "name": "lineitem 2",
                        "order": 2,
                        "pk": 1,
                        "token": 2,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    },
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        json = response.json()
        self.assertDictEqual(
            json, {"lineitems": ["Multiple lineitems have same pk"]}, json
        )
        self.assertEqual(
            Task.objects.count(), 1, "Expected no additionl tasks to be created"
        )
        self.assertEqual(
            LineItem.objects.count(), 0, "Expected no lineitems to be created"
        )

    def test_reject_create_task_with_lineitem_using_existing_token(self):
        self.assertEqual(Task.objects.count(), 0, "Expected zero pre-existing tasks")
        response = self.client.post(
            f"/api/task/job/{self.job.pk}/tasks/",
            {
                "name": "task 1",
                "order": 6,
                "qty": "5.000",
                "unit": "h",
                "price": "25.00",
                "total": "125.00",
                "lineitems": [
                    {
                        "name": "lineitem 1",
                        "order": 1,
                        "token": 1,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        json = response.json()
        self.assertDictEqual(
            json,
            {
                "pk": 1,
                "name": "task 1",
                "description": "",
                "order": 6,
                "qty": "5.000",
                "qty_equation": "",
                "unit": "h",
                "price": "25.00",
                "price_equation": "",
                "total": "125.00",
                "total_equation": "",
                "variant_group": 0,
                "variant_serial": 0,
                "is_provisional": False,
                "parent": 1,
                "lineitems": [
                    {
                        "pk": 1,
                        "token": 1,
                        "name": "lineitem 1",
                        "order": 1,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    }
                ],
            },
            json,
        )

        self.assertEqual(Task.objects.count(), 1, "Expected 1 task to be created")
        self.assertEqual(
            LineItem.objects.count(), 1, "Expected 1 lineitem to be created"
        )

        response = self.client.post(
            f"/api/task/job/{self.job.pk}/tasks/",
            {
                "name": "task 2",
                "order": 6,
                "qty": "5.000",
                "unit": "h",
                "price": "25.00",
                "total": "125.00",
                "lineitems": [
                    {
                        "name": "lineitem with token that already exists",
                        "order": 2,
                        "token": 1,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    }
                ],
            },
            format="json",
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        json = response.json()
        self.assertDictEqual(
            json,
            {"lineitems": [{"token": ["Token already assigned to another lineitem"]}]},
            json,
        )
        self.assertEqual(
            Task.objects.count(), 1, "Expected no addiional task to be created"
        )
        self.assertEqual(
            LineItem.objects.count(), 1, "Expected no additional lineitem to be created"
        )

    def test_reject_create_task_with_lineitem_with_pk(self):
        self.assertEqual(Task.objects.count(), 1, "Expected 1 pre-existing tasks")

        self.assertEqual(
            LineItem.objects.count(), 0, "Expected zero pre-existing lineitems"
        )

        response = self.client.post(
            f"/api/task/job/{self.job.pk}/tasks/",
            {
                "name": "task 1",
                "order": 6,
                "qty": "5.000",
                "unit": "h",
                "price": "25.00",
                "total": "125.00",
                "lineitems": [
                    {
                        "name": "lineitem 1",
                        "order": 1,
                        "pk": 123,
                        "token": 2,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        json = response.json()
        self.assertDictEqual(
            json,
            {
                "lineitems": "Cannot create task with lineitem with a predefined pk, try updating instead"
            },
            json,
        )

        self.assertEqual(
            Task.objects.count(), 1, "Expected no additional task to be created"
        )
        self.assertEqual(
            LineItem.objects.count(), 0, "Expected no additional lineitem to be created"
        )

    def test_reject_update_task_lineitem_using_token(self):
        task1 = TaskFactory(
            group=self.job, name="task 1", qty=1, unit="h", price=19.99, total=19.99
        )
        lineitem1 = LineItemFactory(
            task=task1,
            name="The Line Item",
            qty=1,
            unit="h",
            price=19.99,
            total=19.99,
            token=1,
        )

        self.assertEqual(Task.objects.count(), 1, "Expected 1 pre-existing tasks")
        self.assertEqual(
            LineItem.objects.count(), 1, "Expected 1 pre-existing lineitems"
        )

        response = self.client.patch(
            f"/api/task/job/{self.job.pk}/task/{task1.pk}/",
            {
                "name": "task 1",
                "order": 6,
                "qty": "5.000",
                "unit": "h",
                "price": "25.00",
                "total": "125.00",
                "lineitems": [
                    {
                        "name": "lineitem 1",
                        "order": 1,
                        "token": 1,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        json = response.json()
        self.assertDictEqual(
            json,
            {"lineitems": [{"token": ["Token already assigned to another lineitem"]}]},
            json,
        )

        self.assertEqual(
            Task.objects.count(), 1, "Expected no additional task to be created"
        )
        self.assertEqual(
            LineItem.objects.count(), 1, "Expected no additional lineitem to be created"
        )
        self.assertEqual(
            LineItem.objects.all().first().name,
            "The Line Item",
            "Expected lineitem to not update its name",
        )

    def test_reject_update_task_lineitem_using_invalid_pk(self):
        task1 = TaskFactory(
            group=self.job, name="task 1", qty=1, unit="h", price=19.99, total=19.99
        )
        lineitem1 = LineItemFactory(
            task=task1,
            name="The Line Item",
            qty=1,
            unit="h",
            price=19.99,
            total=19.99,
            token=1,
        )

        self.assertEqual(Task.objects.count(), 1, "Expected 1 pre-existing tasks")
        self.assertEqual(
            LineItem.objects.count(), 1, "Expected 1 pre-existing lineitems"
        )

        response = self.client.patch(
            f"/api/task/job/{self.job.pk}/task/{task1.pk}/",
            {
                "name": "task 1 updated name",
                "order": 6,
                "qty": "5.000",
                "unit": "h",
                "price": "25.00",
                "total": "125.00",
                "lineitems": [
                    {
                        "name": "lineitem 1",
                        "order": 1,
                        "pk": 123456,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND, response.data)
        json = response.json()
        self.assertDictEqual(json, {"detail": "Not found."}, json)

        self.assertEqual(
            Task.objects.count(), 1, "Expected no additional task to be created"
        )
        self.assertEqual(
            LineItem.objects.count(), 1, "Expected no additional lineitem to be created"
        )
        self.assertEqual(
            Task.objects.all().first().name,
            "task 1",
            "Expected task to not update its name",
        )
        self.assertEqual(
            LineItem.objects.all().first().name,
            "The Line Item",
            "Expected lineitem to not update its name",
        )

    def test_update_task_lineitem_using_pk(self):
        task1 = TaskFactory(
            group=self.job, name="task 1", qty=1, unit="h", price=19.99, total=19.99
        )
        lineitem1 = LineItemFactory(
            task=task1,
            name="The Line Item",
            qty=1,
            unit="h",
            price=19.99,
            total=19.99,
            token=1,
        )

        self.assertEqual(Task.objects.count(), 1, "Expected 1 pre-existing tasks")
        self.assertEqual(
            LineItem.objects.count(), 1, "Expected 1 pre-existing lineitems"
        )

        response = self.client.patch(
            f"/api/task/job/{self.job.pk}/task/{task1.pk}/",
            {
                "name": "task 1",
                "order": 6,
                "qty": "5.000",
                "unit": "h",
                "price": "25.00",
                "total": "125.00",
                "lineitems": [
                    {
                        "pk": lineitem1.pk,
                        "name": "lineitem 1",
                        "order": 1,
                        "token": 1,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_200_OK, response.data)
        json = response.json()
        self.assertDictEqual(
            json,
            {
                "pk": 1,
                "name": "task 1",
                "description": "",
                "order": 6,
                "qty": "5.000",
                "qty_equation": "",
                "unit": "h",
                "price": "25.00",
                "price_equation": "",
                "total": "125.00",
                "total_equation": "",
                "variant_group": 0,
                "variant_serial": 0,
                "is_provisional": False,
                "parent": 1,
                "lineitems": [
                    {
                        "pk": 1,
                        "token": 1,
                        "name": "lineitem 1",
                        "order": 1,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    }
                ],
            },
            json,
        )

        self.assertEqual(Task.objects.count(), 1, "Expected 1 task to be created")
        self.assertEqual(
            LineItem.objects.count(), 1, "Expected 1 lineitem to be created"
        )

        self.assertEqual(
            Task.objects.count(), 1, "Expected no addiional task to be created"
        )
        self.assertEqual(
            LineItem.objects.count(), 1, "Expected no additional lineitem to be created"
        )
        self.assertEqual(
            LineItem.objects.all().first().name,
            "lineitem 1",
            "Expected lineitem to update its name",
        )

    def test_update_task_deletes_absent_lineitems(self):

        lineitem1 = LineItemFactory(
            task=self.task,
            name="The Line Item",
            qty=1,
            unit="h",
            price=19.99,
            total=19.99,
            token=1,
        )
        lineitem2 = LineItemFactory(
            task=self.task,
            name="The Line Item 2",
            qty=1,
            unit="h",
            price=19.99,
            total=19.99,
            token=2,
        )

        self.assertEqual(Task.objects.count(), 1, "Expected 1 pre-existing tasks")
        self.assertEqual(
            LineItem.objects.count(), 2, "Expected 2 pre-existing lineitems"
        )

        response = self.client.patch(
            f"/api/task/job/{self.job.pk}/task/{self.task.pk}/",
            {
                "name": "task 1",
                "order": 6,
                "qty": "5.000",
                "unit": "h",
                "price": "50.00",
                "total": "250.00",
                "lineitems": [
                    {
                        "name": "lineitem 2",
                        "order": 1,
                        "pk": lineitem2.pk,
                        "token": 2,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    },
                    {
                        "name": "lineitem 3",
                        "order": 2,
                        "token": 3,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    },
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_200_OK, response.data)
        json = response.json()
        self.assertDictEqual(
            json,
            {
                "pk": self.task.pk,
                "name": "task 1",
                "description": "",
                "order": 6,
                "qty": "5.000",
                "qty_equation": "",
                "unit": "h",
                "price": "50.00",
                "price_equation": "",
                "total": "250.00",
                "total_equation": "",
                "variant_group": 0,
                "variant_serial": 0,
                "is_provisional": False,
                "parent": self.task.group.pk,
                "lineitems": [
                    {
                        "pk": 2,
                        "token": 2,
                        "name": "lineitem 2",
                        "order": 1,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    },
                    {
                        "pk": 3,
                        "token": 3,
                        "name": "lineitem 3",
                        "order": 2,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    },
                ],
            },
            json,
        )

        self.assertEqual(
            Task.objects.count(), 1, "Expected no addiional task to be created"
        )
        self.assertEqual(
            LineItem.objects.count(), 2, "Expected no additional lineitem to be created"
        )

        with self.assertRaises(
            LineItem.DoesNotExist, msg="Expected absent line item to have been deleted"
        ):
            LineItem.objects.get(pk=lineitem1.pk)

    def test_reject_update_task_lineitem_token(self):
        task1 = TaskFactory(
            group=self.job, name="task 1", qty=1, unit="h", price=19.99, total=19.99
        )
        lineitem1 = LineItemFactory(
            task=task1,
            name="The Line Item",
            qty=1,
            unit="h",
            price=19.99,
            total=19.99,
            token=1,
        )

        self.assertEqual(Task.objects.count(), 1, "Expected 1 pre-existing tasks")
        self.assertEqual(
            LineItem.objects.count(), 1, "Expected 1 pre-existing lineitems"
        )

        response = self.client.patch(
            f"/api/task/job/{self.job.pk}/task/{task1.pk}/",
            {
                "name": "task 1",
                "order": 6,
                "qty": "5.000",
                "unit": "h",
                "price": "25.00",
                "total": "125.00",
                "lineitems": [
                    {
                        "pk": lineitem1.pk,
                        "name": "lineitem 1",
                        "order": 1,
                        "token": 55,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_200_OK, response.data)
        json = response.json()
        self.assertDictEqual(
            json,
            {
                "pk": 1,
                "name": "task 1",
                "description": "",
                "order": 6,
                "qty": "5.000",
                "qty_equation": "",
                "unit": "h",
                "price": "25.00",
                "price_equation": "",
                "total": "125.00",
                "total_equation": "",
                "variant_group": 0,
                "variant_serial": 0,
                "is_provisional": False,
                "parent": 1,
                "lineitems": [
                    {
                        "pk": 1,
                        "token": 1,
                        "name": "lineitem 1",
                        "order": 1,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    }
                ],
            },
            json,
        )

        self.assertEqual(Task.objects.count(), 1, "Expected 1 task to be created")
        self.assertEqual(
            LineItem.objects.count(), 1, "Expected 1 lineitem to be created"
        )

        self.assertEqual(
            Task.objects.count(), 1, "Expected no addiional task to be created"
        )
        self.assertEqual(
            LineItem.objects.count(), 1, "Expected no additional lineitem to be created"
        )
        self.assertEqual(
            LineItem.objects.all().first().name,
            "lineitem 1",
            "Expected lineitem to update its name",
        )
        self.assertEqual(
            LineItem.objects.all().first().token,
            1,
            "Expected lineitem token to not be updated",
        )

    def test_reject_create_task_without_token_in_lineitem(self):

        self.assertEqual(Task.objects.count(), 0, "Expected zero pre-existing tasks")

        response = self.client.post(
            f"/api/task/job/{self.job.pk}/tasks/",
            {
                "name": "task 1",
                "order": 6,
                "qty": "5.000",
                "unit": "h",
                "price": "5.00",
                "total": "25.00",
                "lineitems": [
                    {
                        "name": "lineitem 1",
                        "order": 1,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        json = response.json()
        self.assertEqual(
            json,
            {
                "lineitems": [
                    {
                        "pk": ["`pk` is required for updating lineitem"],
                        "token": ["`token` is required for creating lineitem"],
                    }
                ]
            },
            json,
        )

        self.assertEqual(Task.objects.count(), 0, "Expected no tasks to be created")

    def test_reject_create_task_with_mismatch_in_task_price_and_lineitems_total(self):

        self.assertEqual(Task.objects.count(), 0, "Expected zero pre-existing tasks")

        response = self.client.post(
            f"/api/task/job/{self.job.pk}/tasks/",
            {
                "name": "task 1",
                "order": 6,
                "qty": "5.000",
                "unit": "h",
                "price": "5.00",
                "total": "25.00",
                "lineitems": [
                    {
                        "name": "lineitem 1",
                        "order": 1,
                        "token": 1,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    },
                    {
                        "name": "lineitem 2",
                        "order": 2,
                        "token": 2,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    },
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        json = response.json()
        self.assertEqual(
            json, {"price": ["Task price does not match lineitems total"]}, json
        )

        self.assertEqual(Task.objects.count(), 0, "Expected no tasks to be created")

    def test_reject_create_task_with_wrong_task_total(self):

        self.assertEqual(Task.objects.count(), 0, "Expected zero pre-existing tasks")

        response = self.client.post(
            f"/api/task/job/{self.job.pk}/tasks/",
            {
                "name": "task 1",
                "order": 6,
                "qty": "5.000",
                "unit": "h",
                "price": "5.00",
                "total": "20.00",
                "lineitems": [
                    {
                        "name": "lineitem 1",
                        "order": 1,
                        "token": 1,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        json = response.json()
        self.assertEqual(json, {"total": ["Total is not equal to qty*price"]}, json)

        self.assertEqual(Task.objects.count(), 0, "Expected no tasks to be created")

    def test_reject_create_task_with_wrong_lineitem_total(self):

        self.assertEqual(Task.objects.count(), 0, "Expected zero pre-existing tasks")

        response = self.client.post(
            f"/api/task/job/{self.job.pk}/tasks/",
            {
                "name": "task 1",
                "order": 6,
                "qty": "5.000",
                "unit": "h",
                "price": "5.00",
                "total": "25.00",
                "lineitems": [
                    {
                        "name": "lineitem 1",
                        "order": 1,
                        "token": 1,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "20.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        json = response.json()
        self.assertEqual(
            json, {"lineitems": [{"total": ["Total is not equal to qty*price"]}]}, json
        )

        self.assertEqual(Task.objects.count(), 0, "Expected no tasks to be created")

    def test_reject_create_task_without_lineitem(self):
        self.assertEqual(Task.objects.count(), 0, "Expected zero pre-existing tasks")

        response = self.client.post(
            f"/api/task/job/{self.job.pk}/tasks/",
            {
                "name": "task 1",
                "order": 6,
                "qty": "5.000",
                "unit": "h",
                "price": "5.00",
                "total": "25.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        json = response.json()
        self.assertDictEqual(json, {"lineitems": ["This field is required."]}, json)

        self.assertEqual(Task.objects.count(), 0, "Expected no tasks to be created")


class GroupApiTest(ClientTestCase):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.jobsite = JobSiteFactory(project=self.project)
        self.job = JobFactory(project=self.project, name="this is a test job")
        self.group = GroupFactory(parent=self.job, name="this is a test group")

    def test_group_clone(self):
        job = JobFactory(project=ProjectFactory(structure="01.01.001"))
        group = GroupFactory(parent=job, name="Groupy Group")
        job2 = JobFactory(project=ProjectFactory(structure="01.01.001"))
        self.assertEqual(job2.groups.count(), 0)
        response = self.client.post(
            "/api/task/group/clone/",
            {"source": group.pk, "target": job2.pk, "position": 1},
            format="json",
        )
        self.assertEqual(job2.groups.first().name, "Groupy Group")
        self.assertEqual(response.status_code, 200, response.data)
        json = response.json()
        self.assertEqual(
            json,
            {
                "pk": job2.groups.first().pk,
                "name": "Groupy Group",
                "description": "",
                "order": 1,
                "groups": [],
                "tasks": [],
                "parent": job2.pk,
                "job": job2.pk,
            },
            json,
        )

    def test_search_groups(self):
        job = JobFactory(
            name="The Job",
            project=ProjectFactory(structure="01.01.001"),
            generate_groups=True,
        )
        group1 = GroupFactory(parent=job, name="Voranstrich aus Bitumenlösung")

        group2 = GroupFactory(parent=job, name="Schächte und Fundamente")

        response = self.client.post(
            "/api/task/group/search/",
            {"remaining_depth": 0, "terms": "bitumenlos"},
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_200_OK)

        json = response.json()
        self.assertListEqual(
            json,
            [
                {
                    "pk": 5,
                    "name": "Voranstrich aus Bitumenlösung",
                    "description": "",
                    "groups": 0,
                    "tasks": 0,
                }
            ],
            json,
        )

    def test_list_groups(self):
        group1 = GroupFactory(parent=self.job, name="this is a test group 01")
        subgroup1 = GroupFactory(parent=group1, name="this is a test subgroup 01")
        group2 = GroupFactory(parent=self.job, name="this is a test group 02")
        subgroup2 = GroupFactory(parent=group2, name="this is a test subgroup 02")

        serialized_group = flutter.GroupSerializer(instance=self.group).data
        serialized_job = flutter.GroupSerializer(instance=self.job).data
        serialized_group1 = flutter.GroupSerializer(instance=group1).data
        serialized_group2 = flutter.GroupSerializer(instance=group2).data
        serialized_subgroup1 = flutter.GroupSerializer(instance=subgroup1).data
        serialized_subgroup2 = flutter.GroupSerializer(instance=subgroup2).data

        response = self.client.get("/api/task/group/")
        json = response.json()
        self.assertDictEqual(
            json,
            {
                "count": 6,
                "next": None,
                "previous": None,
                "results": [
                    serialized_subgroup2,
                    serialized_subgroup1,
                    serialized_group,
                    serialized_job,
                    serialized_group1,
                    serialized_group2,
                ],
            },
            json,
        )

    def test_list_groups_with_tasks(self):
        group1 = GroupFactory(parent=self.job, name="this is a test group 01")
        subgroup1 = GroupFactory(parent=group1, name="this is a test subgroup 01")
        group2 = GroupFactory(parent=self.job, name="this is a test group 02")
        subgroup2 = GroupFactory(parent=group2, name="this is a test subgroup 02")

        task1 = TaskFactory(
            group=subgroup1, name="task 1", qty=1, unit="h", price=19.99, total=19.99
        )
        task1_lineitem1 = LineItemFactory(
            task=task1,
            name="The Line Item 01",
            qty=1,
            unit="h",
            price=19.99,
            total=19.99,
        )
        task1_lineitem2 = LineItemFactory(
            task=task1,
            name="The Line Item 02",
            qty=1,
            unit="h",
            price=19.99,
            total=19.99,
        )
        task2 = TaskFactory(
            group=subgroup1, name="task 2", qty=1, unit="h", price=19.99, total=19.99
        )
        task2_lineitem1 = LineItemFactory(
            task=task2,
            name="The Line Item 01",
            qty=1,
            unit="h",
            price=19.99,
            total=19.99,
        )
        task2_lineitem2 = LineItemFactory(
            task=task2,
            name="The Line Item 02",
            qty=1,
            unit="h",
            price=19.99,
            total=19.99,
        )

        serialized_group = flutter.GroupSerializer(instance=self.group).data
        serialized_job = flutter.GroupSerializer(instance=self.job).data
        serialized_group1 = flutter.GroupSerializer(instance=group1).data
        serialized_group2 = flutter.GroupSerializer(instance=group2).data
        serialized_subgroup1 = flutter.GroupSerializer(instance=subgroup1).data
        serialized_subgroup2 = flutter.GroupSerializer(instance=subgroup2).data

        response = self.client.get("/api/task/group/")

        self.assertEqual(response.status_code, HTTP_200_OK)

        json = response.json()
        self.assertDictEqual(
            json,
            {
                "count": 6,
                "next": None,
                "previous": None,
                "results": [
                    serialized_subgroup2,
                    serialized_subgroup1,
                    serialized_group,
                    serialized_job,
                    serialized_group1,
                    serialized_group2,
                ],
            },
            json,
        )

    def test_list_subgroups(self):
        subgroup1 = GroupFactory(parent=self.group, name="this is a test subgroup 01")
        subgroup2 = GroupFactory(parent=self.group, name="this is a test subgroup 02")

        response = self.client.get(f"/api/task/group/{self.group.pk}/subgroups/")
        self.assertEqual(response.status_code, HTTP_200_OK)
        json = response.json()
        self.assertDictEqual(
            json[0],
            {
                "pk": subgroup1.pk,
                "name": "this is a test subgroup 01",
                "description": "",
                "order": 1,
                "groups": [],
                "tasks": [],
                "parent": self.group.pk,
                "job": self.job.pk,
            },
            json[0],
        )
        self.assertDictEqual(
            json[1],
            {
                "pk": subgroup2.pk,
                "name": "this is a test subgroup 02",
                "description": "",
                "order": 2,
                "groups": [],
                "tasks": [],
                "parent": self.group.pk,
                "job": self.job.pk,
            },
            json[1],
        )

    def test_create_subgroup_without_order(self):
        response = self.client.post(
            f"/api/task/group/{self.group.pk}/subgroups/", {"name": "test subgroup"}
        )

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        json = response.json()

        self.assertDictEqual(json, {"order": ["This field is required."]}, json)

    def test_create_subgroup(self):
        response = self.client.post(
            f"/api/task/group/{self.group.pk}/subgroups/",
            {"name": "test subgroup", "order": 5},
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        json = response.json()

        self.assertDictEqual(
            json,
            {
                "pk": 3,
                "name": "test subgroup",
                "description": "",
                "order": 5,
                "groups": [],
                "tasks": [],
                "parent": self.group.pk,
                "job": self.job.pk,
            },
            json,
        )

    def test_list_tasks(self):
        task1 = TaskFactory(
            group=self.group, name="task 1", qty=1, unit="h", price=19.99, total=19.99
        )

        task2 = TaskFactory(
            group=self.group, name="task 2", qty=1, unit="pc", price=19.99, total=19.99
        )

        response = self.client.get(f"/api/task/group/{self.group.pk}/tasks/")
        self.assertEqual(response.status_code, HTTP_200_OK)
        json = response.json()
        self.assertDictEqual(
            json[0],
            {
                "pk": task1.pk,
                "name": "task 1",
                "description": "",
                "order": 1,
                "qty": "1.000",
                "qty_equation": "",
                "unit": "h",
                "price": "19.99",
                "price_equation": "",
                "total": "19.99",
                "total_equation": "",
                "variant_group": 0,
                "variant_serial": 0,
                "is_provisional": False,
                "parent": self.group.pk,
                "lineitems": [],
            },
            json[0],
        )
        self.assertDictEqual(
            json[1],
            {
                "pk": task2.pk,
                "name": "task 2",
                "description": "",
                "order": 2,
                "qty": "1.000",
                "qty_equation": "",
                "unit": "pc",
                "price": "19.99",
                "price_equation": "",
                "total": "19.99",
                "total_equation": "",
                "variant_group": 0,
                "variant_serial": 0,
                "is_provisional": False,
                "parent": self.group.pk,
                "lineitems": [],
            },
            json[1],
        )

    def test_create_task(self):
        response = self.client.post(
            f"/api/task/group/{self.group.pk}/tasks/",
            {
                "name": "task 1",
                "order": 6,
                "qty": "5.000",
                "unit": "h",
                "price": "25.00",
                "total": "125.00",
                "lineitems": [
                    {
                        "name": "lineitem 1",
                        "order": 1,
                        "token": 1,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_201_CREATED, response.data)
        json = response.json()
        self.assertDictEqual(
            json,
            {
                "pk": 1,
                "name": "task 1",
                "description": "",
                "order": 6,
                "qty": "5.000",
                "qty_equation": "",
                "unit": "h",
                "price": "25.00",
                "price_equation": "",
                "total": "125.00",
                "total_equation": "",
                "variant_group": 0,
                "variant_serial": 0,
                "is_provisional": False,
                "parent": self.group.pk,
                "lineitems": [
                    {
                        "pk": 1,
                        "name": "lineitem 1",
                        "order": 1,
                        "token": 1,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    }
                ],
            },
            json,
        )

        task = Task.objects.get(pk=json["pk"], group=self.group)

        self.assertEqual(
            task.group.pk, self.group.pk, "Expected task to have correct group.pk"
        )
        self.assertEqual(
            task.job.pk, self.job.pk, "Expected task to have correct job.pk"
        )
        self.assertDictEqual(
            flutter.TaskSerializer(task).data,
            json,
            "Expected saved task to match response",
        )

    def test_reject_create_task_without_lineitem(self):
        self.assertEqual(Task.objects.count(), 0, "Expected zero pre-existing tasks")

        response = self.client.post(
            f"/api/task/group/{self.group.pk}/tasks/",
            {
                "name": "task 1",
                "order": 6,
                "qty": "5.000",
                "unit": "h",
                "price": "5.00",
                "total": "25.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        json = response.json()
        self.assertDictEqual(json, {"lineitems": ["This field is required."]}, json)

        self.assertEqual(Task.objects.count(), 0, "Expected no tasks to be created")

    def test_update_task(self):
        task1 = TaskFactory(
            group=self.group, name="task 1", qty=1, unit="h", price=19.99, total=19.99
        )

        self.assertEqual(Task.objects.count(), 1, "Expected 1 pre-existing tasks")
        self.assertEqual(
            LineItem.objects.count(), 0, "Expected 0 pre-existing lineitems"
        )

        response = self.client.patch(
            f"/api/task/group/{self.group.pk}/task/{task1.pk}/",
            {
                "name": "updated name",
                "order": 6,
                "qty": "5.000",
                "unit": "h",
                "price": "25.00",
                "total": "125.00",
                "lineitems": [
                    {
                        "name": "lineitem 1",
                        "order": 1,
                        "token": 1,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        json = response.json()
        self.assertDictEqual(
            json,
            {
                "pk": 1,
                "name": "updated name",
                "description": "",
                "order": 6,
                "qty": "5.000",
                "qty_equation": "",
                "unit": "h",
                "price": "25.00",
                "price_equation": "",
                "total": "125.00",
                "total_equation": "",
                "variant_group": 0,
                "variant_serial": 0,
                "is_provisional": False,
                "parent": self.group.pk,
                "lineitems": [
                    {
                        "pk": 1,
                        "name": "lineitem 1",
                        "order": 1,
                        "token": 1,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    }
                ],
            },
            json,
        )

        self.assertEqual(
            Task.objects.get(pk=task1.pk).name,
            "updated name",
            "Expected task to have updated name in db",
        )

        self.assertEqual(Task.objects.count(), 1, "Expected no new tasks to be created")
        self.assertEqual(
            LineItem.objects.count(), 1, "Expected 1 lineitem to be created"
        )

        # Repetative updates will not create new lineitems without pk
        # they will fail

        response = self.client.patch(
            f"/api/task/group/{self.group.pk}/task/{task1.pk}/",
            {
                "name": "updated name 2",
                "order": 6,
                "qty": "5.000",
                "unit": "h",
                "price": "25.00",
                "total": "125.00",
                "lineitems": [
                    {
                        "name": "lineitem with updated name",
                        "order": 1,
                        "token": 1,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST, response.data)
        json = response.json()
        self.assertDictEqual(
            json,
            {"lineitems": [{"token": ["Token already assigned to another lineitem"]}]},
            json,
        )

        self.assertEqual(
            Task.objects.get(pk=task1.pk).name,
            "updated name",
            "Expected task to have previous name in db",
        )
        self.assertEqual(
            Task.objects.get(pk=task1.pk).lineitems.first().name,
            "lineitem 1",
            "Expected lineitem to have previous name in db",
        )

        self.assertEqual(Task.objects.count(), 1, "Expected no new tasks to be created")
        self.assertEqual(
            LineItem.objects.count(), 1, "Expected no new lineitem to be created"
        )

    def test_get_task(self):
        task1 = TaskFactory(
            group=self.group, name="task 1", qty=1, unit="h", price=19.99, total=19.99
        )

        response = self.client.get(f"/api/task/group/{self.group.pk}/task/{task1.pk}/")

        self.assertEqual(response.status_code, HTTP_200_OK)
        json = response.json()
        self.assertDictEqual(
            json,
            {
                "pk": task1.pk,
                "name": "task 1",
                "description": "",
                "order": 1,
                "qty": "1.000",
                "qty_equation": "",
                "unit": "h",
                "price": "19.99",
                "price_equation": "",
                "total": "19.99",
                "total_equation": "",
                "variant_group": 0,
                "variant_serial": 0,
                "is_provisional": False,
                "parent": self.group.pk,
                "lineitems": [],
            },
            json,
        )

    def test_delete_task(self):
        task1 = TaskFactory(
            group=self.group, name="task 1", qty=1, unit="h", price=19.99, total=19.99
        )
        self.assertIsNotNone(Task.objects.get(pk=task1.pk))

        response = self.client.delete(
            f"/api/task/group/{self.group.pk}/task/{task1.pk}/"
        )

        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        with self.assertRaises(Task.DoesNotExist):
            Task.objects.get(pk=task1.pk)


class JobApiTest(ClientTestCase):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.jobsite = JobSiteFactory(project=self.project)
        self.job = JobFactory(project=self.project, name="this is a test job")

    def test_list_groups(self):
        group1 = GroupFactory(parent=self.job, name="this is a test group 01")
        group2 = GroupFactory(parent=self.job, name="this is a test group 02")

        response = self.client.get(f"/api/task/job/{self.job.pk}/groups/")
        self.assertEqual(response.status_code, HTTP_200_OK)
        json = response.json()
        self.assertDictEqual(
            json[0],
            {
                "pk": group1.pk,
                "name": "this is a test group 01",
                "description": "",
                "order": 1,
                "groups": [],
                "tasks": [],
                "parent": self.job.pk,
                "job": self.job.pk,
            },
            json[0],
        )
        self.assertDictEqual(
            json[1],
            {
                "pk": group2.pk,
                "name": "this is a test group 02",
                "description": "",
                "order": 2,
                "groups": [],
                "tasks": [],
                "parent": self.job.pk,
                "job": self.job.pk,
            },
            json[1],
        )

    def test_create_group_without_order(self):
        response = self.client.post(
            f"/api/task/job/{self.job.pk}/groups/", {"name": "test group"}
        )

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        json = response.json()

        self.assertDictEqual(json, {"order": ["This field is required."]}, json)

    def test_create_group(self):
        response = self.client.post(
            f"/api/task/job/{self.job.pk}/groups/",
            {"name": "test group", "order": 5},
            format="json",
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        json = response.json()

        self.assertDictEqual(
            json,
            {
                "pk": 2,
                "name": "test group",
                "description": "",
                "order": 5,
                "groups": [],
                "tasks": [],
                "parent": self.job.pk,
                "job": self.job.pk,
            },
            json,
        )

    def test_list_tasks(self):
        task1 = TaskFactory(
            group=self.job, name="task 1", qty=1, unit="h", price=19.99, total=19.99
        )

        task2 = TaskFactory(
            group=self.job, name="task 2", qty=1, unit="pc", price=19.99, total=19.99
        )

        response = self.client.get(f"/api/task/job/{self.job.pk}/tasks/")
        self.assertEqual(response.status_code, HTTP_200_OK)
        json = response.json()
        self.assertDictEqual(
            json[0],
            {
                "pk": task1.pk,
                "name": "task 1",
                "description": "",
                "order": 1,
                "qty": "1.000",
                "qty_equation": "",
                "unit": "h",
                "price": "19.99",
                "price_equation": "",
                "total": "19.99",
                "total_equation": "",
                "variant_group": 0,
                "variant_serial": 0,
                "is_provisional": False,
                "parent": self.job.pk,
                "lineitems": [],
            },
            json[0],
        )
        self.assertDictEqual(
            json[1],
            {
                "pk": task2.pk,
                "name": "task 2",
                "description": "",
                "order": 2,
                "qty": "1.000",
                "qty_equation": "",
                "unit": "pc",
                "price": "19.99",
                "price_equation": "",
                "total": "19.99",
                "total_equation": "",
                "variant_group": 0,
                "variant_serial": 0,
                "is_provisional": False,
                "parent": self.job.pk,
                "lineitems": [],
            },
            json[1],
        )

    def test_create_task(self):
        response = self.client.post(
            f"/api/task/job/{self.job.pk}/tasks/",
            {
                "name": "task 1",
                "order": 6,
                "qty": "5.000",
                "unit": "h",
                "price": "25.00",
                "total": "125.00",
                "lineitems": [
                    {
                        "name": "lineitem 1",
                        "order": 1,
                        "token": 1,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_201_CREATED, response.data)
        json = response.json()
        self.assertDictEqual(
            json,
            {
                "pk": 1,
                "name": "task 1",
                "description": "",
                "order": 6,
                "qty": "5.000",
                "qty_equation": "",
                "unit": "h",
                "price": "25.00",
                "price_equation": "",
                "total": "125.00",
                "total_equation": "",
                "variant_group": 0,
                "variant_serial": 0,
                "is_provisional": False,
                "parent": self.job.pk,
                "lineitems": [
                    {
                        "pk": 1,
                        "name": "lineitem 1",
                        "order": 1,
                        "token": 1,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    }
                ],
            },
            json,
        )

        task = Task.objects.get(pk=json["pk"], group=self.job)

        self.assertEqual(
            task.group.pk, self.job.pk, "Expected task to have correct group.pk"
        )
        self.assertEqual(
            task.job.pk, self.job.pk, "Expected task to have correct job.pk"
        )
        self.assertDictEqual(
            flutter.TaskSerializer(task).data,
            json,
            "Expected saved task to match response",
        )

    def test_update_task(self):
        task1 = TaskFactory(
            group=self.job, name="task 1", qty=1, unit="h", price=19.99, total=19.99
        )

        self.assertEqual(Task.objects.count(), 1, "Expected 1 pre-existing tasks")
        self.assertEqual(
            LineItem.objects.count(), 0, "Expected 0 pre-existing lineitems"
        )

        response = self.client.patch(
            f"/api/task/job/{self.job.pk}/task/{task1.pk}/",
            {
                "name": "updated name",
                "order": 6,
                "qty": "5.000",
                "unit": "h",
                "price": "25.00",
                "total": "125.00",
                "lineitems": [
                    {
                        "name": "lineitem 1",
                        "order": 1,
                        "token": 1,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_200_OK, response.data)
        json = response.json()
        self.assertDictEqual(
            json,
            {
                "pk": 1,
                "name": "updated name",
                "description": "",
                "order": 6,
                "qty": "5.000",
                "qty_equation": "",
                "unit": "h",
                "price": "25.00",
                "price_equation": "",
                "total": "125.00",
                "total_equation": "",
                "variant_group": 0,
                "variant_serial": 0,
                "is_provisional": False,
                "parent": self.job.pk,
                "lineitems": [
                    {
                        "pk": 1,
                        "name": "lineitem 1",
                        "order": 1,
                        "token": 1,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    }
                ],
            },
            json,
        )

        self.assertEqual(
            Task.objects.get(pk=task1.pk).name,
            "updated name",
            "Expected task to have updated name in db",
        )

        self.assertEqual(Task.objects.count(), 1, "Expected no new tasks to be created")
        self.assertEqual(
            LineItem.objects.count(), 1, "Expected 1 lineitem to be created"
        )

        # Repetative updates will not create new lineitems without pk
        # they will fail

        response = self.client.patch(
            f"/api/task/job/{self.job.pk}/task/{task1.pk}/",
            {
                "name": "updated name 2",
                "order": 6,
                "qty": "5.000",
                "unit": "h",
                "price": "25.00",
                "total": "125.00",
                "lineitems": [
                    {
                        "name": "lineitem with updated name",
                        "order": 1,
                        "token": 1,
                        "qty": "5.000",
                        "qty_equation": "",
                        "unit": "h",
                        "price": "5.00",
                        "price_equation": "",
                        "total": "25.00",
                        "total_equation": "",
                        "is_hidden": False,
                        "lineitem_type": "other",
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST, response.data)
        json = response.json()
        self.assertDictEqual(
            json,
            {"lineitems": [{"token": ["Token already assigned to another lineitem"]}]},
            json,
        )

        self.assertEqual(
            Task.objects.get(pk=task1.pk).name,
            "updated name",
            "Expected task to have previous name in db",
        )
        self.assertEqual(
            Task.objects.get(pk=task1.pk).lineitems.first().name,
            "lineitem 1",
            "Expected lineitem to have previous name in db",
        )

        self.assertEqual(Task.objects.count(), 1, "Expected no new tasks to be created")
        self.assertEqual(
            LineItem.objects.count(), 1, "Expected no new lineitem to be created"
        )

    def test_get_task(self):
        task1 = TaskFactory(
            group=self.job, name="task 1", qty=1, unit="h", price=19.99, total=19.99
        )

        response = self.client.get(f"/api/task/job/{self.job.pk}/task/{task1.pk}/")

        self.assertEqual(response.status_code, HTTP_200_OK)
        json = response.json()
        self.assertDictEqual(
            json,
            {
                "pk": task1.pk,
                "name": "task 1",
                "description": "",
                "order": 1,
                "qty": "1.000",
                "qty_equation": "",
                "unit": "h",
                "price": "19.99",
                "price_equation": "",
                "total": "19.99",
                "total_equation": "",
                "variant_group": 0,
                "variant_serial": 0,
                "is_provisional": False,
                "parent": self.job.pk,
                "lineitems": [],
            },
            json,
        )

    def test_delete_task(self):
        task1 = TaskFactory(
            group=self.job, name="task 1", qty=1, unit="h", price=19.99, total=19.99
        )
        self.assertIsNotNone(Task.objects.get(pk=task1.pk))

        response = self.client.delete(f"/api/task/job/{self.job.pk}/task/{task1.pk}/")

        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        with self.assertRaises(Task.DoesNotExist):
            Task.objects.get(pk=task1.pk)
