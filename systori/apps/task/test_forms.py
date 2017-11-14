from django.test import TestCase
from django.utils.translation import activate
from django.core.files.uploadedfile import File

from ..company.models import Company
from ..project.models import Project

from ..company.factories import CompanyFactory
from ..project.factories import ProjectFactory
from .gaeb.tests import get_test_data_path
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


class JobImportTest(TestCase):

    def setUp(self):
        CompanyFactory()

    def test_import_add_jobs(self):
        project = ProjectFactory(with_job=True)
        job = project.jobs.get()
        path = get_test_data_path('25144280.x83')
        form = JobImportForm(
            project=project,
            data={},
            files={'file': File(path.open())}
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(project.jobs.count(), 1)
        form.save()
        self.assertEqual(project.jobs.count(), 2)
        new_job = project.jobs.exclude(pk=job.pk).get()
        self.assertEqual("Dachdecker- und Klempnerarbeiten", new_job.name)
        self.assertTrue(new_job.account)
