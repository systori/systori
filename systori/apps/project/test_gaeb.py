import os.path

from django.conf import settings
from django.test import TestCase
from django.core.exceptions import ValidationError

from ..company.factories import CompanyFactory
from ..project.factories import ProjectFactory
from ..task.factories import JobFactory

from .models import Project
from .forms import GAEBImportForm
from .gaeb import GAEBStructure, GAEBStructureField
from .gaeb_utils import gaeb_import


class GAEBStructureTests(TestCase):

    def test_task_formatting(self):
        struct = GAEBStructure("9.01.02.0009")
        self.assertEqual('0001', struct.format_task(1))
        self.assertEqual('12345', struct.format_task(12345))

    def test_group_formatting(self):
        struct = GAEBStructure("9.000.00.0000")
        self.assertEqual('1', struct.format_group(1, 0))
        self.assertEqual('099', struct.format_group(99, 1))
        self.assertEqual('99', struct.format_group(99, 2))

    def test_is_valid_depth(self):
        struct = GAEBStructure("9.000.00.0000")
        self.assertEqual(struct.is_valid_depth(-1), False)
        self.assertEqual(struct.is_valid_depth(0), True)
        self.assertEqual(struct.is_valid_depth(1), True)
        self.assertEqual(struct.is_valid_depth(2), True)
        self.assertEqual(struct.is_valid_depth(3), False)
        self.assertEqual(struct.is_valid_depth(4), False)

    def test_depth(self):
        gaeb = GAEBStructure
        self.assertEqual(gaeb('0.0').maximum_depth, 0)
        self.assertEqual(gaeb('0.0.0').maximum_depth, 1)
        self.assertEqual(gaeb('0.0.0.0').maximum_depth, 2)


class GAEBStructureFieldTests(TestCase):

    def test_valid(self):
        GAEBStructureField().clean('0.0', None)
        GAEBStructureField().clean('01.0001.0001.001.0.0', None)

    def test_empty(self):
        with self.assertRaisesMessage(ValidationError, 'cannot be blank'):
            GAEBStructureField().clean('', None)

    def test_too_short(self):
        with self.assertRaisesMessage(ValidationError, 'outside the allowed hierarchy'):
            GAEBStructureField().clean('0', None)

    def test_too_long(self):
        with self.assertRaisesMessage(ValidationError, 'outside the allowed hierarchy'):
            GAEBStructureField().clean('01.0001.0001.001.0.0.0', None)

    def test_depth_field(self):

        project = Project(structure='01.01.001')
        self.assertEquals(project.structure.pattern, '01.01.001')
        self.assertEquals(project.structure_depth, 1)

        # setting `structure` automatically updates `structure_depth`
        project.structure = '01.01.01.001'
        self.assertEquals(project.structure_depth, 2)

        # structure str automatically get converted to GAEBStructure
        self.assertIsInstance(project.structure, GAEBStructure)

        # directly setting `structure_depth` is a no-op
        project.structure_depth = 99
        self.assertEquals(project.structure_depth, 2)


class GaebImportTests(TestCase):

    def setUp(self):
        CompanyFactory()
        self.form = GAEBImportForm()

    def test_import(self):
        file_path = os.path.join(settings.BASE_DIR, "apps/project/test_data/gaeb.x83")
        project = gaeb_import(file_path, self.form)
        self.assertEqual("7030 Herschelbad", project.name)

    def test_import2(self):
        file_path = os.path.join(settings.BASE_DIR, "apps/project/test_data/25144280.x83")
        project = gaeb_import(file_path, self.form)
        self.assertEqual("Dachinstandsetzung", project.name)

    def test_import_add_jobs(self):
        project = ProjectFactory()
        JobFactory(project=project)
        file_path = os.path.join(settings.BASE_DIR, "apps/project/test_data/25144280.x83")
        project = gaeb_import(file_path, self.form, project)
        self.assertEqual(project.jobs.all().count(), 2)
