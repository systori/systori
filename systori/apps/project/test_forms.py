from django.core.files.uploadedfile import File
from django.test import TestCase
from django.utils.translation import activate

from systori.apps.task.gaeb.tests import get_test_data_path
from . import forms
from .factories import ProjectFactory, JobSiteFactory
from .models import JobSite
from ..company.factories import CompanyFactory


class ProjectFormTest(TestCase):
    def setUp(self):
        self.company = CompanyFactory()

    def test_create_required_field_validation(self):
        activate("en")
        form = forms.ProjectCreateForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            {
                "name": ["This field is required."],
                "structure": ["This field is required."],
            },
            form.errors,
        )

    def test_create_structure_validation(self):
        activate("en")

        def errors(s):
            form = forms.ProjectCreateForm(data={"structure": s})
            self.assertIn("structure", form.errors, "No validation error triggered.")
            return form.errors["structure"]

        self.assertEqual(errors(""), ["GAEB hierarchy cannot be blank."])
        self.assertEqual(
            errors("0"), ["GAEB hierarchy is outside the allowed hierarchy depth."]
        )

    def test_create_save(self):
        form = forms.ProjectCreateForm(
            data={"name": "new project", "structure": "01.0.0.0"}
        )
        self.assertTrue(form.is_valid())
        project = form.save()
        self.assertEquals(project.structure_depth, 2)

    def test_update_save(self):
        project = ProjectFactory(name="new project")
        self.assertEqual(project.name, "new project")
        form = forms.ProjectUpdateForm(
            data={"name": "updated project", "structure": "0.0.0"}, instance=project
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        project.refresh_from_db()
        self.assertEquals(project.structure_depth, 1)
        self.assertEqual(project.name, "updated project")

    def test_update_structure_validation(self):
        activate("en")
        project = ProjectFactory(name="new project")

        def errors(s):
            form = forms.ProjectUpdateForm(data={"structure": s}, instance=project)
            self.assertIn("structure", form.errors, "No validation error triggered.")
            return form.errors["structure"]

        self.assertEqual(errors(""), ["GAEB hierarchy cannot be blank."])
        self.assertEqual(
            errors("0"), ["GAEB hierarchy is outside the allowed hierarchy depth."]
        )
        self.assertEqual(
            errors("0.0.0.0"), ["Cannot change depth after project has been created."]
        )


class JobSiteFormTest(TestCase):
    def setUp(self):
        self.company = CompanyFactory()

    def test_create_required_field_validation(self):
        activate("en")
        form = forms.JobSiteForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            {
                "name": ["This field is required."],
                "address": ["This field is required."],
                "city": ["This field is required."],
                "postal_code": ["This field is required."],
            },
            form.errors,
        )

    def test_create_save(self):
        form = forms.JobSiteForm(
            data={
                "name": "new jobsite",
                "address": "1 Fake Ave",
                "city": "Village",
                "postal_code": "12345",
            },
            instance=JobSite(project=ProjectFactory()),
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(0, JobSite.objects.count())
        form.save()
        self.assertEqual(1, JobSite.objects.count())

    def test_update_save(self):
        jobsite = JobSiteFactory(project=ProjectFactory())
        self.assertNotEqual(jobsite.name, "updated jobsite")
        form = forms.JobSiteForm(
            data={
                "name": "updated jobsite",
                "address": "1 Fake Ave",
                "city": "Village",
                "postal_code": "12345",
            },
            instance=jobsite,
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        jobsite.refresh_from_db()
        self.assertEqual(jobsite.name, "updated jobsite")


class ProjectImportTests(TestCase):
    def setUp(self):
        CompanyFactory()

    def test_import(self):
        path = get_test_data_path("gaeb.x83")
        form = forms.ProjectImportForm(data={}, files={"file": File(path.open())})
        self.assertTrue(form.is_valid())
        project = form.save()
        self.assertEqual("7030 Herschelbad", project.name)
