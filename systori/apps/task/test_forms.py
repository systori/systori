from django.test import TestCase
from django.utils.translation import activate

from ..company.models import Company
from ..project.models import Project
from ..task.models import Job

from ..company.factories import CompanyFactory
from ..project.factories import ProjectFactory
from ..user.factories import UserFactory
from .factories import GroupFactory
from .forms import *


class JobFormTest(TestCase):

    def setUp(self):
        self.company = CompanyFactory()  # type: Company
        self.project = ProjectFactory()  # type: Project

    def test_required_field_validation(self):
        activate('en')

        form = JobTemplateCreateForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual({
            'name': ['This field is required.'],
        }, form.errors)

        form = JobCreateForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual({
            'name': ['This field is required.'],
        }, form.errors)

    def test_save(self):

        form = JobTemplateCreateForm(data={
            'name': 'job tpl',
            'description': 'sample job description'
        }, instance=Job(project=Project.objects.template().get()))
        self.assertTrue(form.is_valid())
        template = form.save()

        GroupFactory(parent=template, name='group template')

        self.assertEqual(
            template.name,
            list(JobCreateForm().fields['job_template'].choices)[1][1])

        # Using Template
        form = JobCreateForm(data={
            'name': 'new job',
            'job_template': template.pk
        }, instance=Job(project=self.project))
        self.assertTrue(form.is_valid())
        new_job = form.save()
        self.assertEquals('group template', new_job.groups.first().name)

        # Not Using Template
        form = JobCreateForm(data={
            'name': 'new job 2',
        }, instance=Job(project=self.project))
        self.assertTrue(form.is_valid())
        new_job = form.save()
        self.assertEquals(0, new_job.groups.count())

        job = Job.objects.get(id=new_job.id)
        self.assertEquals('02', job.code)


class JobProgressFormTest(TestCase):

    def setUp(self):
        self.company = CompanyFactory()  # type: Company
        self.project = ProjectFactory()  # type: Project
        self.user = UserFactory(company=self.company, language='en')
        self.worker = self.user.access.first()

    def test_at_least_one_option_checked(self):
        form = JobProgressForm(data={
            'progress_worker': self.worker.id
        })
        self.assertFalse(form.is_valid())
        self.assertEqual({
            '__all__': ['At least one option is required.'],
        }, form.errors)

    def test_status_complete_doesnt_require_progress_fields(self):
        form = JobProgressForm(data={'status_complete': 'true'})
        self.assertTrue(form.is_valid(), form.errors)

    def test_progress_onehundred_requires_other_fields(self):
        form = JobProgressForm(data={
            'progress_onehundred': 'true',
        })
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEqual({
            'progress_date': ['Required when setting progress to 100%.'],
            'progress_worker': ['Required when setting progress to 100%.'],
            'comment': ['Required when setting progress to 100%.'],
        }, form.errors)
