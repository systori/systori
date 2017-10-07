from django.urls import reverse

from systori.lib.testing import ClientTestCase

from ..project.factories import ProjectFactory

from .factories import JobFactory, TaskFactory, LineItemFactory
from .models import Job, ProgressReport, ExpendReport


class JobViewsTest(ClientTestCase):

    def test_create(self):
        project = ProjectFactory()
        self.assertEqual(Job.objects.count(), 0)
        response = self.client.post(
            reverse('job.create', args=[project.pk]),
            data={'name': 'New Job'}
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

    def test_delete(self):
        job = JobFactory(project=ProjectFactory())
        self.assertEqual(Job.objects.count(), 1)
        response = self.client.post(
            reverse('job.delete', args=[job.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Job.objects.count(), 0)


class JobProgressTest(ClientTestCase):

    def setUp(self):
        super().setUp()
        self.job = JobFactory(
            name='job name',
            description='new job description',
            project=ProjectFactory()
        )  # type: Job

    def test_get_form(self):
        self.client.get(
            reverse('job.progress', args=[self.job.project.pk, self.job.pk]),
        )

    def test_status_complete_happy_path(self):
        self.assertEqual(self.job.status, Job.DRAFT)
        response = self.client.post(
            reverse('job.progress', args=[self.job.project.pk, self.job.pk]),
            {'status_complete': 'true'}
        )
        self.assertEqual(response.status_code, 302)
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, Job.COMPLETED)

    def test_change_task_progress(self):
        task = TaskFactory(group=self.job, qty=10, price=5, total=50)

        job = Job.objects.get()
        self.assertEqual(job.progress_percent, 0)
        self.assertEqual(ProgressReport.objects.count(), 0)

        response = self.client.post(
            reverse('job.progress', args=[self.job.project.pk, self.job.pk]), {
                'progress_onehundred': 'true',
                'progress_date': '01/01/2001',
                'comment': 'default comment',
                'task-{}-complete'.format(task.id): 10,
                'task-{}-worker'.format(task.id): self.worker.id,
                'task-{}-comment'.format(task.id): 'specific comment'
            }
        )
        self.assertEqual(response.status_code, 302)
        job = Job.objects.get()
        self.assertEqual(job.status, Job.DRAFT)
        self.assertEqual(job.progress_percent, 100)
        progress = ProgressReport.objects.get()
        self.assertEqual(progress.task, task)
        self.assertEqual(progress.complete, 10)
        self.assertEqual(progress.comment, 'specific comment')
        self.assertEqual(progress.worker, self.worker)

    def test_change_task_progress_default_comment(self):
        task = TaskFactory(group=self.job, qty=10, price=5, total=50)
        self.client.post(
            reverse('job.progress', args=[self.job.project.pk, self.job.pk]), {
                'progress_date': '01/01/2001',
                'comment': 'default comment',
                'task-{}-complete'.format(task.id): 10,
                'task-{}-worker'.format(task.id): self.worker.id,
                'task-{}-comment'.format(task.id): ''
            }
        )
        progress = ProgressReport.objects.get()
        self.assertEqual(progress.comment, 'default comment')

    def test_change_lineitem_progress(self):
        task = TaskFactory(group=self.job, qty=None, price=5, total=50)
        lineitem = LineItemFactory(task=task, qty=10, price=5, total=50)

        job = Job.objects.get()
        self.assertEqual(job.progress_percent, 0)
        self.assertEqual(ExpendReport.objects.count(), 0)

        response = self.client.post(
            reverse('job.progress', args=[self.job.project.pk, self.job.pk]), {
                'progress_date': '01/01/2001',
                'comment': 'default comment',
                'li-{}-expended'.format(lineitem.id): 10,
                'li-{}-worker'.format(lineitem.id): self.worker.id,
                'li-{}-comment'.format(lineitem.id): 'specific comment',
            }
        )
        self.assertEqual(response.status_code, 302)
        job = Job.objects.get()
        self.assertEqual(job.status, Job.DRAFT)
        self.assertEqual(job.progress_percent, 100)
        expend = ExpendReport.objects.get()
        self.assertEqual(expend.lineitem, lineitem)
        self.assertEqual(expend.expended, 10)
        self.assertEqual(expend.comment, 'specific comment')
        self.assertEqual(expend.worker, self.worker)


class JobCopyTest(ClientTestCase):

    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.job = JobFactory(
            name='job name',
            description='new job description',
            project=self.project
        )  # type: Job

    def test_copy_job_regular(self):
        response = self.client.get(
            reverse('job.copy', args=[self.project.pk])
        )
        form = response.context['form']
        self.assertFalse(form.is_valid())
        response = self.client.post(
            reverse('job.copy', args=[self.project.pk]),
            {'job_id':self.job.pk}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.project.jobs.count(), 2)

    def test_error_on_incompatible_structure(self):
        self.project2 = ProjectFactory(structure="01.001")
        response = self.client.post(
            reverse('job.copy', args=[self.project2.pk]),
            {'job_id': self.job.pk}
        ) # fails because of incompatible project.structure
        self.assertEqual(self.project2.jobs.count(), 0)
        self.job2 = JobFactory(project=self.project2) #creates first job on project2
        response = self.client.post(
            reverse('job.copy', args=[self.project2.pk]),
            {'job_id': self.job2.pk}
        ) # creates second job on project2
        self.assertEqual(self.project2.jobs.count(), 2)

