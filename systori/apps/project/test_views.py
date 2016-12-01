from django.core.urlresolvers import reverse

from systori.lib.testing import ClientTestCase

from ..task.factories import JobFactory
from .factories import ProjectFactory
from .models import Project


class TestProjectListView(ClientTestCase):

    def test_load_without_search_term(self):
        response = self.client.get(reverse('projects'), {})
        self.assertEqual(200, response.status_code)

    def test_load_with_search_term(self):
        response = self.client.get(reverse('projects'), {'search_term': 'one two'})
        self.assertEqual(200, response.status_code)


class TestProgressViews(ClientTestCase):

    def test_project_progress(self):
        project = ProjectFactory()
        response = self.client.get(reverse('project.progress', args=[project.id]), {})
        self.assertEqual(200, response.status_code)

    def test_project_progress_all(self):
        response = self.client.get(reverse('project.progress.all'), {})
        self.assertEqual(200, response.status_code)


class TestProjectViews(ClientTestCase):

    def test_create_project(self):

        response = self.client.get(reverse('project.create'), {})
        self.assertEqual(200, response.status_code)

        response = self.client.post(reverse('project.create'), {
            'name': 'new test project',
            'address': 'One Street',
            'city': 'Town',
            'postal_code': '12345',
            'structure_format': '0.0',
        })
        self.assertEqual(302, response.status_code)
        self.assertTrue(Project.objects.filter(name='new test project').exists())

    def test_view_project(self):
        project = ProjectFactory()
        JobFactory(project=project)
        response = self.client.get(reverse('project.view', args=[project.pk]), {})
        self.assertEqual(200, response.status_code)
