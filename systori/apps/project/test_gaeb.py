import os.path

from django.conf import settings
from django.test import TestCase

from ..company.factories import CompanyFactory

from .models import GAEBHierarchyStructure
from .gaeb_utils import gaeb_import


class GAEBStructureTests(TestCase):

    def test_task_formatting(self):
        struct = GAEBHierarchyStructure("9.01.02.0009")
        self.assertEqual('0001', struct.format_task(1))
        self.assertEqual('12345', struct.format_task(12345))

    def test_group_formatting(self):
        struct = GAEBHierarchyStructure("9.000.00.0000")
        self.assertEqual('1', struct.format_group(1, 0))
        self.assertEqual('099', struct.format_group(99, 1))
        self.assertEqual('99', struct.format_group(99, 2))

    def test_has_level(self):
        struct = GAEBHierarchyStructure("9.000.00.0000")
        self.assertEqual(struct.has_level(-1), False)
        self.assertEqual(struct.has_level(0), True)
        self.assertEqual(struct.has_level(1), True)
        self.assertEqual(struct.has_level(2), True)
        self.assertEqual(struct.has_level(3), False)
        self.assertEqual(struct.has_level(4), False)

    def test_depth(self):
        gaeb = GAEBHierarchyStructure
        self.assertEqual(gaeb('0.0').depth, 0)
        self.assertEqual(gaeb('0.0.0').depth, 1)
        self.assertEqual(gaeb('0.0.0.0').depth, 2)


class GaebImportTests(TestCase):

    def setUp(self):
        CompanyFactory()

    def test_import(self):
        file_path = os.path.join(settings.BASE_DIR, "apps/project/test_data/gaeb.x83")
        project = gaeb_import(file_path)
        self.assertEqual("7030 Herschelbad", project.name)

    def test_import2(self):
        file_path = os.path.join(settings.BASE_DIR, "apps/project/test_data/25144280.x83")
        project = gaeb_import(file_path)
        self.assertEqual("Dachinstandsetzung", project.name)
