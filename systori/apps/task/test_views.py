from django.urls import reverse

from systori.lib.testing import ClientTestCase

from ..project.factories import ProjectFactory

from .factories import JobFactory, TaskFactory, LineItemFactory
from .models import Job


class JobViewsTest(ClientTestCase):

    def test_create(self):
        project = ProjectFactory()
        self.assertEqual(Job.objects.count(), 0)
        response = self.client.post(
            reverse('job.create', args=[project.pk]),
            data={'name': 'New Job', 'billing_method': Job.FIXED_PRICE}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Job.objects.count(), 1)

    def test_get_editor(self):
        job = JobFactory(
            name='job name',
            description='new job description',
            project=ProjectFactory()
        )  # type: Job
        self.assertEqual(
            reverse('job.editor', args=[job.project.pk, job.pk]),
            job.get_absolute_url()
        )
        response = self.client.get(job.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'new job description', response.content)
        self.assertEqual(response.context['job'], job)

    def test_transition(self):
        job = JobFactory(
            name='job name',
            description='new job description',
            project=ProjectFactory()
        )  # type: Job

        self.assertEqual(job.status, Job.DRAFT)
        for action, phase in [('propose', Job.PROPOSED), ('approve', Job.APPROVED)]:
            response = self.client.get(
                reverse('job.transition', args=[job.project.pk, job.pk, action])
            )
            self.assertEqual(response.status_code, 302)
            job.refresh_from_db()
            self.assertEqual(job.status, phase)

    def test_delete(self):
        job = JobFactory(project=ProjectFactory())
        self.assertEqual(Job.objects.count(), 1)
        response = self.client.post(
            reverse('job.delete', args=[job.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Job.objects.count(), 0)
