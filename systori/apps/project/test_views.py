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
