from django.test import TestCase
from django.utils.translation import activate

from ..company.factories import CompanyFactory
from .factories import ProjectFactory
from . import forms


class ProjectFormTest(TestCase):

    def setUp(self):
        self.company = CompanyFactory()

    def test_create_validation(self):
        activate('en')

        form = forms.ProjectCreateForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual({
            'name': ['This field is required.'],
            'structure_format': ['This field is required.'],
            'address': ['This field is required.'],
            'city': ['This field is required.'],
            'postal_code': ['This field is required.'],
        }, form.errors)

    def test_create_save(self):
        form = forms.ProjectCreateForm(data={
            'name': 'new project',
            'structure_format': '01.0',
            'address': '1 Fake Ave',
            'city': 'Village',
            'postal_code': '12345'
        })
        self.assertTrue(form.is_valid())
        project = form.save()
        self.assertEquals(len(project.jobs.all()), 1)
        self.assertEquals(project.jobs.first().code, '01')
        self.assertEquals(len(project.jobsites.all()), 1)

    def test_update_save(self):
        project = ProjectFactory(name='new project')
        self.assertEqual(project.name, 'new project')
        form = forms.ProjectUpdateForm(data={
            'name': 'updated project',
            'structure_format': '0.0',
        }, instance=project)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        project.refresh_from_db()
        self.assertEqual(project.name, 'updated project')
