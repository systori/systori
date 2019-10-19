from decimal import Decimal
from django.urls import reverse
from systori.lib.testing import ClientTestCase
from .models import Group, Task, LineItem
from ..project.factories import ProjectFactory
from .factories import JobFactory, GroupFactory, TaskFactory, LineItemFactory


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
                "pk": 1,
                "token": None,
                "name": job.name,
                "description": "",
                "order": 1,
                "groups": [
                    {
                        "pk": 2,
                        "token": 9006199254740991,
                        "name": "test group",
                        "description": "",
                        "order": 5,
                        "groups": [
                            {
                                "pk": 3,
                                "token": 9006199254740992,
                                "name": "sub group",
                                "description": "",
                                "order": 7,
                                "groups": [],
                                "tasks": [],
                                "parent": 2,
                                "job": 1,
                            },
                            {
                                "pk": 4,
                                "token": 9006199254740993,
                                "name": "sub group 2",
                                "description": "",
                                "order": 8,
                                "groups": [
                                    {
                                        "pk": 5,
                                        "token": 9006199254740994,
                                        "name": "sub sub group",
                                        "description": "",
                                        "order": 1,
                                        "groups": [],
                                        "tasks": [],
                                        "parent": 4,
                                        "job": 1,
                                    }
                                ],
                                "tasks": [],
                                "parent": 2,
                                "job": 1,
                            },
                        ],
                        "tasks": [],
                        "parent": 1,
                        "job": 1,
                    }
                ],
                "tasks": [],
                "parent": None,
                "job": 1,
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
                "pk": 1,
                "token": None,
                "name": job.name,
                "description": "",
                "order": 1,
                "groups": [
                    {
                        "pk": 2,
                        "token": 7,
                        "name": "test group",
                        "description": "",
                        "order": 1,
                        "groups": [
                            {
                                "pk": 3,
                                "token": 8,
                                "name": "sub group",
                                "description": "",
                                "order": 1,
                                "groups": [],
                                "tasks": [],
                                "parent": 2,
                                "job": 1,
                            }
                        ],
                        "tasks": [],
                        "parent": 1,
                        "job": 1,
                    }
                ],
                "tasks": [],
                "parent": None,
                "job": 1,
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
                "pk": 1,
                "token": None,
                "name": job.name,
                "description": "",
                "order": 1,
                "groups": [
                    {
                        "pk": 2,
                        "token": 7,
                        "name": "test group",
                        "description": "",
                        "order": 1,
                        "groups": [
                            {
                                "pk": 3,
                                "token": 8,
                                "name": "sub group",
                                "description": "",
                                "order": 1,
                                "groups": [],
                                "tasks": [],
                                "parent": 2,
                                "job": 1,
                            }
                        ],
                        "tasks": [],
                        "parent": 1,
                        "job": 1,
                    }
                ],
                "tasks": [],
                "parent": None,
                "job": 1,
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
                "pk": 1,
                "token": None,
                "name": job.name,
                "description": "",
                "order": 1,
                "groups": [
                    {
                        "pk": 3,
                        "token": None,
                        "name": "group 2 for update",
                        "description": "",
                        "order": 1,
                        "groups": [],
                        "tasks": [],
                        "parent": 1,
                        "job": 1,
                    },
                    {
                        "pk": 2,
                        "token": None,
                        "name": "updated group",
                        "description": "",
                        "order": 2,
                        "groups": [],
                        "tasks": [],
                        "parent": 1,
                        "job": 1,
                    },
                ],
                "tasks": [],
                "parent": None,
                "job": 1,
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
                "name": job.name,
                "description": "",
                "order": 1,
                "groups": [],
                "tasks": [
                    {
                        "pk": 1,
                        "token": 9006199254740991,
                        "name": "test task",
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
                        "job": 1,
                        "group": 1,
                        "lineitems": [
                            {
                                "pk": 1,
                                "token": 9006199254740992,
                                "name": "lineitem",
                                "order": 1,
                                "qty": "0.000",
                                "qty_equation": "",
                                "unit": "",
                                "price": "0.00",
                                "price_equation": "",
                                "total": "0.00",
                                "total_equation": "",
                                "is_hidden": False,
                                "lineitem_type": "other",
                                "task": 1,
                                "job": 1,
                            },
                            {
                                "pk": 2,
                                "token": 9006199254740993,
                                "name": "lineitem 2",
                                "order": 2,
                                "qty": "0.000",
                                "qty_equation": "",
                                "unit": "",
                                "price": "0.00",
                                "price_equation": "",
                                "total": "0.00",
                                "total_equation": "",
                                "is_hidden": False,
                                "lineitem_type": "other",
                                "task": 1,
                                "job": 1,
                            },
                        ],
                    }
                ],
                "parent": None,
                "job": 1,
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
                "name": job.name,
                "description": "",
                "order": 1,
                "groups": [],
                "tasks": [
                    {
                        "pk": 1,
                        "token": 9006199254740991,
                        "name": "test task",
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
                        "job": 1,
                        "group": 1,
                        "lineitems": [
                            {
                                "pk": 1,
                                "token": 9006199254740992,
                                "name": "lineitem",
                                "order": 1,
                                "qty": "0.000",
                                "qty_equation": "",
                                "unit": "",
                                "price": "0.00",
                                "price_equation": "",
                                "total": "0.00",
                                "total_equation": "",
                                "is_hidden": False,
                                "lineitem_type": "other",
                                "task": 1,
                                "job": 1,
                            },
                            {
                                "pk": 2,
                                "token": 9006199254740993,
                                "name": "lineitem 2",
                                "order": 2,
                                "qty": "0.000",
                                "qty_equation": "",
                                "unit": "",
                                "price": "0.00",
                                "price_equation": "",
                                "total": "0.00",
                                "total_equation": "",
                                "is_hidden": False,
                                "lineitem_type": "other",
                                "task": 1,
                                "job": 1,
                            },
                        ],
                    }
                ],
                "parent": None,
                "job": 1,
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
                "name": job.name,
                "description": "",
                "order": 1,
                "groups": [],
                "tasks": [
                    {
                        "pk": 1,
                        "token": None,
                        "name": task.name,
                        "description": "",
                        "order": 1,
                        "qty": "0.000",
                        "qty_equation": "",
                        "unit": "",
                        "price": "0.00",
                        "price_equation": "",
                        "total": "11.00",
                        "total_equation": "",
                        "variant_group": 0,
                        "variant_serial": 0,
                        "is_provisional": False,
                        "job": 1,
                        "group": 1,
                        "lineitems": [
                            {
                                "pk": 1,
                                "token": None,
                                "name": task.lineitems.all()[0].name,
                                "order": 1,
                                "qty": "0.000",
                                "qty_equation": "",
                                "unit": "",
                                "price": "0.00",
                                "price_equation": "",
                                "total": "22.00",
                                "total_equation": "",
                                "is_hidden": False,
                                "lineitem_type": "other",
                                "task": 1,
                                "job": 1,
                            }
                        ],
                    }
                ],
                "parent": None,
                "job": 1,
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
