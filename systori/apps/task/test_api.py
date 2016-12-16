from django.core.urlresolvers import reverse
from systori.lib.testing import ClientTestCase
from .models import Group, Task, LineItem
from ..project.factories import ProjectFactory
from .factories import JobFactory, GroupFactory, TaskFactory, LineItemFactory


class EditorApiTest(ClientTestCase):

    def test_create_group(self):
        job = JobFactory(project=ProjectFactory())
        response = self.client.post(
            reverse('api.editor.save', args=(job.pk,)), {
                'groups': [{
                    'token': 7, 'name': 'test group',
                    'groups': [
                        {'token': 8, 'name': 'sub group'},
                        {'token': 9, 'name': 'sub group 2', 'groups': [
                            {'token': 10, 'name': 'sub sub group'},
                        ]}
                    ]
                }]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(5, Group.objects.count())
        group = Group.objects.get(parent=job)
        self.assertEqual('test group', group.name)
        self.assertEqual('sub group', group.groups.all()[0].name)
        self.assertEqual('sub group 2', group.groups.all()[1].name)
        self.assertEqual('sub sub group', group.groups.all()[1].groups.all()[0].name)
        self.maxDiff = None
        self.assertDictEqual({
            'token': None, 'pk': 1,
            'groups': [{
                'token': 7, 'pk': 2,
                'groups': [
                    {'token': 8, 'pk': 3},
                    {'token': 9, 'pk': 4, 'groups': [
                        {'token': 10, 'pk': 5},
                    ]}
                ]
            }]
        }, response.data)

    def test_create_group_idempotent(self):
        job = JobFactory(project=ProjectFactory())

        response = self.client.post(
            reverse('api.editor.save', args=(job.pk,)), {
                'groups': [{
                    'token': 7, 'name': 'test group',
                    'groups': [{'token': 8, 'name': 'sub group'}]
                }]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(3, Group.objects.count())
        self.assertDictEqual({
            'token': None, 'pk': 1,
            'groups': [{
                'token': 7, 'pk': 2,
                'groups': [{'token': 8, 'pk': 3}]
            }]
        }, response.data)

        response = self.client.post(
            reverse('api.editor.save', args=(job.pk,)), {
                'groups': [{
                    'token': 7, 'name': 'test group',
                    'groups': [{'token': 8, 'name': 'sub group'}]
                }]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(3, Group.objects.count())
        self.assertDictEqual({
            'token': None, 'pk': 1,
            'groups': [{
                'token': 7, 'pk': 2,
                'groups': [{'token': 8, 'pk': 3}]
            }]
        }, response.data)

    def test_update_group(self):
        job = JobFactory(project=ProjectFactory())
        group = GroupFactory(name='group for update', parent=job)
        self.assertEqual(2, Group.objects.count())
        self.assertEqual('group for update', group.name)

        response = self.client.post(
            reverse('api.editor.save', args=(job.pk,)), {
                'groups': [{'pk': group.pk, 'name': 'updated group'}]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200, response.data)

        group.refresh_from_db()
        self.assertEqual(2, Group.objects.count())
        self.assertEqual('updated group', group.name)
        self.assertDictEqual({
            'token': None, 'pk': 1,
            'groups': [{'token': None, 'pk': group.pk}]
        }, response.data)

    def test_delete_group(self):
        project = ProjectFactory(structure="0.0.0.0")
        job = JobFactory(project=project)
        job.generate_groups()
        self.assertEqual(3, Group.objects.count())
        response = self.client.post(
            reverse('api.editor.save', args=(job.pk,)), {
                'delete': {'groups': [2]}
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(1, Group.objects.count())

    def test_create_task_idempotent(self):
        job = JobFactory(project=ProjectFactory())
        response = self.client.post(
            reverse('api.editor.save', args=(job.pk,)), {
                'tasks': [{
                    'token': 5, 'name': 'test task', 'description': '',
                    'qty_equation': '', 'unit': '', 'price_equation': '', 'total_equation': '',
                    'lineitems': [
                        {'token': 6, 'name': 'lineitem', 'qty_equation': '', 'unit': '', 'price_equation': '', 'total_equation': ''},
                        {'token': 7, 'name': 'lineitem 2', 'qty_equation': '', 'unit': '', 'price_equation': '', 'total_equation': ''},
                    ]
                }]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(1, Group.objects.count())
        self.assertEqual(1, Task.objects.count())
        self.assertEqual(2, LineItem.objects.count())
        task = job.tasks.all()[0]
        self.assertEqual('test task', task.name)
        self.assertEqual('lineitem', task.lineitems.all()[0].name)
        self.assertEqual('lineitem 2', task.lineitems.all()[1].name)
        self.assertDictEqual({
            'pk': 1, 'token': None,
            'tasks': [{
                'pk': 1, 'token': 5,
                'lineitems': [
                    {'token': 6, 'pk': 1},
                    {'token': 7, 'pk': 2},
                ]
            }]
        }, response.data)

        response = self.client.post(
            reverse('api.editor.save', args=(job.pk,)), {
                'tasks': [{
                    'token': 5, 'name': 'test task', 'description': '',
                    'qty_equation': '', 'unit': '', 'price_equation': '', 'total_equation': '',
                    'lineitems': [
                        {'token': 6, 'name': 'lineitem', 'qty_equation': '', 'unit': '', 'price_equation': '', 'total_equation': ''},
                        {'token': 7, 'name': 'lineitem 2', 'qty_equation': '', 'unit': '', 'price_equation': '', 'total_equation': ''},
                    ]
                }]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(1, Group.objects.count())
        self.assertEqual(1, Task.objects.count())
        self.assertEqual(2, LineItem.objects.count())
        task = job.tasks.all()[0]
        self.assertEqual('test task', task.name)
        self.assertEqual('lineitem', task.lineitems.all()[0].name)
        self.assertEqual('lineitem 2', task.lineitems.all()[1].name)
        self.assertDictEqual({
            'pk': 1, 'token': None,
            'tasks': [{
                'pk': 1, 'token': 5,
                'lineitems': [
                    {'token': 6, 'pk': 1},
                    {'token': 7, 'pk': 2},
                ]
            }]
        }, response.data)

    def test_delete_task(self):
        job = JobFactory(project=ProjectFactory(structure="0.0.0.0"))
        TaskFactory(group=job)
        TaskFactory(group=job)
        self.assertEqual(2, Task.objects.count())
        response = self.client.post(
            reverse('api.editor.save', args=(job.pk,)), {
                'delete': {'tasks': [1]}
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(1, Task.objects.count())

    def test_update_task(self):
        job = JobFactory(project=ProjectFactory())
        task = TaskFactory(group=job)
        lineitem = LineItemFactory(task=task)
        response = self.client.post(
            reverse('api.editor.save', args=(job.pk,)), {
                'tasks': [{
                    'pk': task.pk, 'total': 11,
                    'lineitems': [
                        {'pk': lineitem.pk, 'total': 22}
                    ]
                }]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200, response.data)
        task = job.tasks.all()[0]
        self.assertEqual(11, task.total)
        self.assertEqual(22, task.lineitems.all()[0].total)
        self.assertDictEqual({
            'pk': 1, 'token': None,
            'tasks': [{
                'pk': 1, 'token': None,
                'lineitems': [{'pk': 1, 'token': None}]
            }]
        }, response.data)

    def test_delete_lineitem(self):
        job = JobFactory(project=ProjectFactory())
        task = TaskFactory(group=job)
        LineItemFactory(task=task)
        LineItemFactory(task=task)
        self.assertEqual(2, LineItem.objects.count())
        response = self.client.post(
            reverse('api.editor.save', args=(job.pk,)), {
                'delete': {'lineitems': [1]}
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(1, LineItem.objects.count())


class AutocompleteApiTest(ClientTestCase):

    def test_group_completion(self):
        job = JobFactory(project=ProjectFactory(structure='01.01.001'), generate_groups=True)
        GroupFactory(parent=job, name='Voranstrich aus Bitumenlösung')
        GroupFactory(parent=job, name='Schächte und Fundamente')
        response = self.client.post(
            reverse('api.editor.autocomplete'), {
                'model_type': 'group',
                'position': 1,
                'terms': 'bitumenlos'
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200, response.data)
        print(response.data)
