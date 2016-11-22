import json
from django.core.urlresolvers import reverse
from systori.lib.testing import SystoriTestCase
from .models import Group, Task, LineItem
from ..company.factories import CompanyFactory
from ..user.factories import UserFactory
from ..project.factories import ProjectFactory
from .factories import JobFactory, GroupFactory, TaskFactory, LineItemFactory


class BaseTestCase(SystoriTestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.worker = UserFactory(company=self.company, language='en', password='open sesame').access.first()
        self.client.login(username=self.worker.email, password='open sesame')


class GroupApiTest(BaseTestCase):

    def test_create(self):
        job = JobFactory(project=ProjectFactory())
        response = self.client.post(
            reverse('group-list'), {
                'job': job.pk, 'token': 7, 'parent': job.pk, 'name': 'test group',
                'groups': [
                    {'job': job.pk, 'token': 8, 'name': 'sub group'},
                    {'job': job.pk, 'token': 9, 'name': 'sub group 2', 'groups': [
                        {'job': job.pk, 'token': 10, 'name': 'sub sub group'},
                    ]}
                ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(5, Group.objects.count())
        group = Group.objects.get(parent=job)
        self.assertEqual('test group', group.name)
        self.assertEqual('sub group', group.groups.all()[0].name)
        self.assertEqual('sub group 2', group.groups.all()[1].name)
        self.assertEqual('sub sub group', group.groups.all()[1].groups.all()[0].name)
        self.assertDictEqual({
            'job': job.pk, 'token': 7, 'pk': 2,
            'groups': [
                {'job': job.pk, 'token': 8, 'pk': 3},
                {'job': job.pk, 'token': 9, 'pk': 4, 'groups': [
                    {'job': job.pk, 'token': 10, 'pk': 5},
                ]}
            ]
        }, response.data)

    def test_create_idempotent(self):
        job = JobFactory(project=ProjectFactory())

        response = self.client.post(
            reverse('group-list'), {
                'job': job.pk, 'token': 7, 'parent': job.pk, 'name': 'test group',
                'groups': [{ 'job': job.pk, 'token': 8, 'name': 'sub group'}]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(3, Group.objects.count())
        self.assertDictEqual({
            'job': job.pk, 'token': 7, 'pk': 2,
            'groups': [{'job': job.pk, 'token': 8, 'pk': 3}]
        }, response.data)

        response = self.client.post(
            reverse('group-list'), {
                'job': job.pk, 'token': 7, 'parent': job.pk, 'name': 'test group',
                'groups': [{ 'job': job.pk, 'token': 8, 'name': 'sub group'}]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(3, Group.objects.count())
        self.assertDictEqual({
            'job': job.pk, 'token': 7, 'pk': 2,
            'groups': [{'job': job.pk, 'token': 8, 'pk': 3}]
        }, response.data)

    def test_update(self):
        group = GroupFactory(name='group for update')
        response = self.client.patch(
            reverse('group-detail', args=[group.pk]),
            {'name': 'updated group'},
            format='json'
        )
        self.assertEqual(response.status_code, 200, response.data)
        group.refresh_from_db()
        self.assertEqual('updated group', group.name)
        self.assertDictEqual({'pk': group.id}, response.data)

    def test_delete(self):
        project = ProjectFactory(structure_format="0.0.0.0")
        job = JobFactory(project=project)
        job.generate_groups()
        self.assertEqual(3, Group.objects.count())
        response = self.client.delete(reverse('group-detail', args=[2]), format='json')
        self.assertEqual(response.status_code, 204, response.data)
        self.assertEqual(1, Group.objects.count())


class TaskApiTest(BaseTestCase):

    def test_create(self):
        job = JobFactory(project=ProjectFactory())
        response = self.client.post(
            reverse('task-list'), {
                'job': job.pk, 'token': 5, 'group': job.pk,
                'name': 'test task', 'description': '',
                'qty_equation': '', 'unit': '', 'price_equation': '', 'total_equation': '',
                'lineitems': [
                    {'job': job.pk, 'token': 6, 'name': 'lineitem', 'qty_equation': '', 'unit': '', 'price_equation': '', 'total_equation': ''},
                    {'job': job.pk, 'token': 7, 'name': 'lineitem 2', 'qty_equation': '', 'unit': '', 'price_equation': '', 'total_equation': ''},
                ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(1, Task.objects.count())
        self.assertEqual(2, LineItem.objects.count())
        task = job.tasks.all()[0]
        self.assertEqual('test task', task.name)
        self.assertEqual('lineitem', task.lineitems.all()[0].name)
        self.assertEqual('lineitem 2', task.lineitems.all()[1].name)
        self.assertDictEqual({
            'job': job.pk, 'token': 5, 'pk': 1,
            'lineitems': [
                {'job': job.pk, 'token': 6, 'pk': 1},
                {'job': job.pk, 'token': 7, 'pk': 2}
            ]
        }, response.data)

    def test_create_idempotent(self):
        job = JobFactory(project=ProjectFactory())

        response = self.client.post(
            reverse('task-list'), {
                'job': job.pk, 'group': job.pk, 'token': 5,
                'name': 'test task',
                'lineitems': [
                    {'job': job.pk, 'token': 6},
                    {'job': job.pk, 'token': 7}
                ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(1, Task.objects.count())
        self.assertEqual(2, LineItem.objects.count())
        self.assertDictEqual({
            'job': job.pk, 'token': 5, 'pk': 1,
            'lineitems': [
                {'job': job.pk, 'token': 6, 'pk': 1},
                {'job': job.pk, 'token': 7, 'pk': 2}
            ]
        }, response.data)

        response = self.client.post(
            reverse('task-list'), {
                'job': job.pk, 'group': job.pk, 'token': 5,
                'name': 'test task',
                'lineitems': [
                    {'job': job.pk, 'token': 6},
                    {'job': job.pk, 'token': 7}
                ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(1, Task.objects.count())
        self.assertEqual(2, LineItem.objects.count())
        self.assertDictEqual({
            'job': job.pk, 'token': 5, 'pk': 1,
            'lineitems': [
                {'job': job.pk, 'token': 6, 'pk': 1},
                {'job': job.pk, 'token': 7, 'pk': 2}
            ]
        }, response.data)

    def test_delete(self):
        job = JobFactory(project=ProjectFactory(structure_format="0.0.0.0"))
        job.generate_groups()
        self.assertEqual(3, Group.objects.count())
        response = self.client.delete(reverse('group-detail', args=[2]), format='json')
        self.assertEqual(response.status_code, 204, response.data)
        self.assertEqual(1, Group.objects.count())

    def test_update(self):
        group = JobFactory(project=ProjectFactory())
        task = TaskFactory(group=group)
        lineitem = LineItemFactory(task=task)
        response = self.client.patch(
            reverse('task-detail', args=[task.pk]), {
                'total': 11,
                'lineitems': [
                    {'pk': lineitem.pk, 'total': 22},
                ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200, response.data)
        task = group.tasks.all()[0]
        self.assertEqual(11, task.total)
        self.assertEqual(22, task.lineitems.all()[0].total)
        self.assertDictEqual({
            'pk': 1,
            'lineitems': [
                {'pk': 1},
            ]
        }, response.data)


class LineItemApiTest(BaseTestCase):

    def test_delete(self):
        task = TaskFactory(group=JobFactory(project=ProjectFactory()))
        LineItemFactory(task=task)
        LineItemFactory(task=task)
        self.assertEqual(2, LineItem.objects.count())
        response = self.client.delete(reverse('lineitem-detail', args=[2]), format='json')
        self.assertEqual(response.status_code, 204, response.data)
        self.assertEqual(1, LineItem.objects.count())
