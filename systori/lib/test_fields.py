from decimal import Decimal
from django.test import TestCase
from django.utils.translation import activate
from django.core.exceptions import ValidationError
from .fields import SmartDecimalField, sanitize_separators


class SmartDecimalFieldTest(TestCase):

    def test_to_python_de(self):
        activate('de')
        field = SmartDecimalField(localize=True)

        self.assertEqual(field.to_python('10000,5001'), Decimal('10000.5001'))
        self.assertEqual(field.to_python('10.000.000,50'), Decimal('10000000.50'))
        with self.assertRaises(ValidationError):
            self.assertEqual(field.to_python('10 000 000,50'), Decimal('10000000.50'))

    def test_to_python_en(self):
        activate('en')
        field = SmartDecimalField(localize=True)

        self.assertEqual(field.to_python('10000.5001'), Decimal('10000.5001'))
        self.assertEqual(field.to_python('10,000,000.50'), Decimal('10000000.50'))
        self.assertEqual(field.to_python('10,000,000.50001'), Decimal('10000000.50001'))
        with self.assertRaises(ValidationError):
            self.assertEqual(field.to_python('10 000 000,50'), Decimal('10000000.50'))


class SanitizeSeparatorsTest(TestCase):

    def test_sanitize_separators_en(self):
        activate('en')

        self.assertEqual('1', sanitize_separators('1'))
        self.assertEqual('1.00', sanitize_separators('1.00'))
        self.assertEqual('1.10', sanitize_separators('1.10'))
        self.assertEqual('1.01', sanitize_separators('1.01'))
        self.assertEqual('1.010', sanitize_separators('1.010'))
        self.assertEqual('1.001', sanitize_separators('1.001'))
        self.assertEqual('1.0001', sanitize_separators('1.0001'))
        self.assertEqual('1.00010', sanitize_separators('1.00010'))
        self.assertEqual('1234567891.0004', sanitize_separators('1,234,567,891.0004'))

    def test_sanitize_separators_de(self):
        activate('de')

        self.assertEqual('1.00', sanitize_separators('1,00'))
        self.assertEqual('1.10', sanitize_separators('1,10'))
        self.assertEqual('1.01', sanitize_separators('1,01'))
        self.assertEqual('1.001', sanitize_separators('1,001'))
        self.assertEqual('1.0001', sanitize_separators('1,0001'))
        self.assertEqual('1234567891.0004', sanitize_separators('1.234.567.891,0004'))
