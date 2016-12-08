from django.core.urlresolvers import reverse

from systori.lib.testing import ClientTestCase

from ..document.factories import ProposalFactory, LetterheadFactory
from ..task.factories import JobFactory

from .factories import ProjectFactory, JobSiteFactory
from .models import Project, JobSite


class TestProjectListView(ClientTestCase):

    def test_load_without_search_term(self):
        response = self.client.get(reverse('projects'))
        self.assertEqual(200, response.status_code)

    def test_load_expected_variables(self):
        ProjectFactory()
        response = self.client.get(reverse('projects'))
        for element in ['sys-sort-button', 'sys-phase-button', 'sys-project-tile']:
            self.assertContains(response, element)
        for phase in dict(Project.PHASE_CHOICES).keys():
            self.assertContains(response, phase)


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

        data = {
            'name': 'new test project',
            'address': 'One Street',
            'city': 'Town',
            'postal_code': '12345',
            'structure': '0.0',
        }

        response = self.client.post(reverse('project.create'), data)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse('projects'))
        self.assertTrue(Project.objects.filter(name='new test project').exists())

        data['save_goto_project'] = ''
        response = self.client.post(reverse('project.create'), data)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse('project.view', args=[3]))

    def test_view_project(self):
        project = ProjectFactory()
        job = JobFactory(project=project)
        proposal = ProposalFactory(
            project=project,
            letterhead=LetterheadFactory(),
        )
        proposal.jobs.add(job)
        response = self.client.get(reverse('project.view', args=[project.pk]), {})
        self.assertEqual(200, response.status_code)

    def test_phase_transition(self):
        project = ProjectFactory()
        self.assertEqual(project.phase, Project.PROSPECTIVE)
        for action, phase in [('begin_tendering', Project.TENDERING), ('begin_planning', Project.PLANNING)]:
            response = self.client.get(
                reverse('project.transition.phase', args=[project.pk, action])
            )
            self.assertEqual(response.status_code, 302)
            project.refresh_from_db()
            self.assertEqual(project.phase, phase)

    def test_state_transition(self):
        project = ProjectFactory()
        self.assertEqual(project.state, Project.ACTIVE)
        for action, state in [('pause', Project.PAUSED), ('stop', Project.STOPPED)]:
            response = self.client.get(
                reverse('project.transition.state', args=[project.pk, action])
            )
            self.assertEqual(response.status_code, 302)
            project.refresh_from_db()
            self.assertEqual(project.state, state)


class TestJobSiteViews(ClientTestCase):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        JobSiteFactory(project=self.project)

    def test_create_jobsite(self):

        response = self.client.get(reverse('jobsite.create', args=[self.project.pk]), {})
        self.assertEqual(200, response.status_code)

        data = {
            'name': '1st floor',
            'address': 'One Street',
            'city': 'Town',
            'postal_code': '12345',
        }

        response = self.client.post(reverse('jobsite.create', args=[self.project.pk]), data)
        self.assertEqual(302, response.status_code)
        self.assertTrue(JobSite.objects.filter(name='1st floor').exists())
