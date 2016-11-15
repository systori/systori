from django.core.urlresolvers import reverse
from systori.lib.testing import SystoriTestCase
from .models import Group, Task, LineItem
from ..company.factories import CompanyFactory
from ..user.factories import UserFactory
from .factories import GroupFactory


class GroupApiTest(SystoriTestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.worker = UserFactory(company=self.company, language='en', password='open sesame').access.first()
        self.client.login(username=self.worker.email, password='open sesame')

    def test_post(self):
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
        print(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(4, Group.objects.count())
        group = Group.objects.get(parent=None)
        self.assertEqual('test group', group.name)
        self.assertEqual('sub group', group.groups.all()[0].name)
        self.assertEqual('sub group 2', group.groups.all()[1].name)
        self.assertEqual('sub sub group', group.groups.all()[1].groups.all()[0].name)
