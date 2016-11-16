from django.core.urlresolvers import reverse
from systori.lib.testing import SystoriTestCase
from .models import Group, Task, LineItem
from ..company.factories import CompanyFactory
from ..user.factories import UserFactory
from ..project.factories import ProjectFactory
from .factories import JobFactory, GroupFactory


class BaseTestCase(SystoriTestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.worker = UserFactory(company=self.company, language='en', password='open sesame').access.first()
        self.client.login(username=self.worker.email, password='open sesame')


class GroupApiTest(BaseTestCase):

    def test_create(self):
        response = self.client.post(
            reverse('group-list'), {
                'name': 'test group',
                'groups': [
                    {'name': 'sub group'},
                    {'name': 'sub group 2', 'groups': [
                        {'name': 'sub sub group'},
                    ]}
                ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(4, Group.objects.count())
        group = Group.objects.get(parent=None)
        self.assertEqual('test group', group.name)
        self.assertEqual('sub group', group.groups.all()[0].name)
        self.assertEqual('sub group 2', group.groups.all()[1].name)
        self.assertEqual('sub sub group', group.groups.all()[1].groups.all()[0].name)

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


class TaskApiTest(BaseTestCase):

    def test_create(self):
        group = GroupFactory(name='group for update', parent=JobFactory(project=ProjectFactory()))
        response = self.client.post(
            reverse('task-list'), {
                'group': group.pk,
                'name': 'test task', 'description': '',
                'qty_equation': '', 'unit': '', 'price_equation': '', 'total_equation': '',
                'lineitems': [
                    {'name': 'lineitem', 'qty_equation': '', 'unit': '', 'price_equation': '', 'total_equation': ''},
                    {'name': 'lineitem 2', 'qty_equation': '', 'unit': '', 'price_equation': '', 'total_equation': ''},
                ]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(1, Task.objects.count())
        self.assertEqual(2, LineItem.objects.count())
        task = group.tasks.all()[0]
        self.assertEqual('test task', task.name)
        self.assertEqual('lineitem', task.lineitems.all()[0].name)
        self.assertEqual('lineitem 2', task.lineitems.all()[1].name)

