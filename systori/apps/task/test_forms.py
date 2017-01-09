from django.test import TestCase
from django.utils.translation import activate

from ..company.models import Company
from ..project.models import Project
from ..task.models import Job

from ..company.factories import CompanyFactory
from ..project.factories import ProjectFactory
from .factories import GroupFactory
from . import forms


class JobFormTest(TestCase):

    def setUp(self):
        self.company = CompanyFactory()  # type: Company
        self.project = ProjectFactory()  # type: Project

    def test_required_field_validation(self):
        activate('en')

        form = forms.JobTemplateCreateForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual({
            'name': ['This field is required.'],
        }, form.errors)

        form = forms.JobCreateForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual({
            'name': ['This field is required.'],
            'billing_method': ['This field is required.'],
        }, form.errors)

    def test_save(self):

        form = forms.JobTemplateCreateForm(data={
            'name': 'job tpl',
            'description': 'sample job description'
        }, instance=Job(project=Project.objects.template().get()))
        self.assertTrue(form.is_valid())
        template = form.save()

        GroupFactory(parent=template, name='group template')

        self.assertEqual(
            template.name,
            list(forms.JobCreateForm().fields['job_template'].choices)[1][1])

        # Using Template
        form = forms.JobCreateForm(data={
            'name': 'new job',
            'billing_method': Job.FIXED_PRICE,
            'job_template': template.pk
        }, instance=Job(project=self.project))
        self.assertTrue(form.is_valid())
        new_job = form.save()
        self.assertEquals('group template', new_job.groups.first().name)

        # Not Using Template
        form = forms.JobCreateForm(data={
            'name': 'new job 2',
            'billing_method': Job.FIXED_PRICE,
        }, instance=Job(project=self.project))
        self.assertTrue(form.is_valid())
        new_job = form.save()
        self.assertEquals(0, new_job.groups.count())

        job = Job.objects.get(id=new_job.id)
        self.assertEquals('02', job.code)
