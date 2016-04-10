from django.core.urlresolvers import reverse

from systori.lib.testing import SystoriTestCase
from ..task.test_models import create_task_data


class TestProjectListView(SystoriTestCase):

    def setUp(self):
        create_task_data(self)
        self.client.login(username=self.user.email, password='open sesame')

    def test_load_without_search_term(self):
        response = self.client.get(reverse('projects'), {})
        self.assertEqual(200, response.status_code)

    def test_load_with_search_term(self):
        response = self.client.get(reverse('projects'), {'search_term': 'one two'})
        self.assertEqual(200, response.status_code)


class TestProjectFormViews(SystoriTestCase):

    def setUp(self):
        create_task_data(self)
        self.client.login(username=self.user.email, password='open sesame')

    def test_create_project(self):
        response = self.client.get(reverse('project.create'), {})
        self.assertEqual(200, response.status_code)

        response = self.client.post(reverse('project.create'), {
            'name': 'new test project',
            'address': 'One Street',
            'city': 'Town',
            'postal_code': '12345',
            'job_zfill': '1',
            'task_zfill': '1',
            'taskgroup_zfill': '1',
            'skip_geocoding': 'True'
        })
        self.assertEqual(302, response.status_code)
