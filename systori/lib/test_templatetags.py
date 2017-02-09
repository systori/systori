from django.test import TestCase
from django.utils.translation import activate
from .templatetags.customformatting import *


class CustomFormattingTest(TestCase):

    def test_ubrdecimal_en(self):
        activate('en')

        self.assertEqual('1.00', ubrdecimal(Decimal('1')))
        self.assertEqual('10.00', ubrdecimal(Decimal('10')))

        self.assertEqual('1.00', ubrdecimal(Decimal('1.0')))
        self.assertEqual('1.10', ubrdecimal(Decimal('1.1')))

        self.assertEqual('1.00', ubrdecimal(Decimal('1.00')))
        self.assertEqual('1.01', ubrdecimal(Decimal('1.01')))
        self.assertEqual('1.01', ubrdecimal(Decimal('1.010')))

        self.assertEqual('1.00', ubrdecimal(Decimal('1.000')))
        self.assertEqual('1.001', ubrdecimal(Decimal('1.001')))
        self.assertEqual('1.001', ubrdecimal(Decimal('1.0010')))

        self.assertEqual('1.0001', ubrdecimal(Decimal('1.0001')))
        self.assertEqual('1.0001', ubrdecimal(Decimal('1.00010')))

        self.assertEqual('1.00', ubrdecimal(Decimal('1.00001')))
        self.assertEqual('1.00', ubrdecimal(Decimal('1.000010')))

        self.assertEqual('1,234,567,891.0004', ubrdecimal(Decimal('1234567891.000400')))

        self.assertEqual('1,000', ubrdecimal(Decimal('1000'), 2, 0))
        self.assertEqual('1,000.01', ubrdecimal(Decimal('1000.009'), 2, 0))

    def test_ubrdecimal_de(self):
        activate('de')

        self.assertEqual('1,00', ubrdecimal(Decimal('1')))
        self.assertEqual('10,00', ubrdecimal(Decimal('10')))

        self.assertEqual('1,00', ubrdecimal(Decimal('1.0')))
        self.assertEqual('1,10', ubrdecimal(Decimal('1.1')))

        self.assertEqual('1,00', ubrdecimal(Decimal('1.00')))
        self.assertEqual('1,01', ubrdecimal(Decimal('1.01')))
        self.assertEqual('1,01', ubrdecimal(Decimal('1.010')))

        self.assertEqual('1,00', ubrdecimal(Decimal('1.000')))
        self.assertEqual('1,001', ubrdecimal(Decimal('1.001')))
        self.assertEqual('1,001', ubrdecimal(Decimal('1.0010')))

        self.assertEqual('1,0001', ubrdecimal(Decimal('1.0001')))
        self.assertEqual('1,0001', ubrdecimal(Decimal('1.00010')))

        self.assertEqual('1,00', ubrdecimal(Decimal('1.00001')))
        self.assertEqual('1,00', ubrdecimal(Decimal('1.000010')))

        self.assertEqual('1.234.567.891,0004', ubrdecimal(Decimal('1234567891.000400')))

        self.assertEqual('1.000', ubrdecimal(Decimal('1000'), 2, 0))
        self.assertEqual('1.000,01', ubrdecimal(Decimal('1000.009'), 2, 0))

    def test_split_rows_vertical(self):
        self.assertEqual([], split_rows_vertically([], 1))
        self.assertEqual([], split_rows_vertically([], 2))
        self.assertEqual([['A']], split_rows_vertically(['A'], 1))
        self.assertEqual([['A', '']], split_rows_vertically(['A'], 2))
        self.assertEqual([['A', 'C'], ['B', '']], split_rows_vertically(['A', 'B', 'C'], 2))
        self.assertEqual([['A', 'C'], ['B', 'D']], split_rows_vertically(['A', 'B', 'C', 'D'], 2))
        self.assertEqual([['A'], ['B'], ['C'], ['D']], split_rows_vertically(['A', 'B', 'C', 'D'], 1))
        self.assertEqual([['A', 'C', ''], ['B', 'D', '']], split_rows_vertically(['A', 'B', 'C', 'D'], 3))
        self.assertEqual([['A', 'B', 'C', 'D']], split_rows_vertically(['A', 'B', 'C', 'D'], 4))
        self.assertEqual([['A', 'B', 'C', 'D']], split_rows_vertically(['A', 'B', 'C', 'D'], 4))
        self.assertEqual([['A', 'C', 'E'], ['B', 'D', '']], split_rows_vertically(['A', 'B', 'C', 'D', 'E'], 3))

    def test_split_rows_horizontally(self):
        self.assertEqual([], split_rows_horizontally([], 1))
        self.assertEqual([], split_rows_horizontally([], 2))
        self.assertEqual([['A']], split_rows_horizontally(['A'], 1))
        self.assertEqual([['A', '']], split_rows_horizontally(['A'], 2))
        self.assertEqual([['A', 'B'], ['C', '']], split_rows_horizontally(['A', 'B', 'C'], 2))
        self.assertEqual([['A', 'B'], ['C', 'D']], split_rows_horizontally(['A', 'B', 'C', 'D'], 2))
        self.assertEqual([['A'], ['B'], ['C'], ['D']], split_rows_horizontally(['A', 'B', 'C', 'D'], 1))
        self.assertEqual([['A', 'B', 'C'], ['D', '', '']], split_rows_horizontally(['A', 'B', 'C', 'D'], 3))
        self.assertEqual([['A', 'B', 'C', 'D']], split_rows_horizontally(['A', 'B', 'C', 'D'], 4))
