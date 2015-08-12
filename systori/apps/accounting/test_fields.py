from decimal import Decimal
from django.test import TestCase
from .fields import SmartDecimalField


class SmartDecimalFieldTest(TestCase):

    def test_to_python(self):
        field = SmartDecimalField()
        self.assertEqual(field.to_python('10000,50'), Decimal('10000.50'))
        self.assertEqual(field.to_python('10000.50'), Decimal('10000.50'))
        self.assertEqual(field.to_python('10 000 000.50'), Decimal('10000000.50'))
        self.assertEqual(field.to_python('10,000,000,50'), Decimal('10000000.50'))
        self.assertEqual(field.to_python('10.000.000.50'), Decimal('10000000.50'))
        self.assertEqual(field.to_python('10.000.000,50'), Decimal('10000000.50'))
