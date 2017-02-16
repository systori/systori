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

    def test_workdaysverbose(self):
        activate('en')
        self.assertEqual(workdaysverbose(60 * 60 * 8), '1 day')
        self.assertEqual(workdaysverbose(60 * 60 * 20), '2.5 days')
        activate('de')
        self.assertEqual(workdaysverbose(60 * 60 * 8), '1 Tag')
        self.assertEqual(workdaysverbose(60 * 60 * 20), '2,5 Tage')

    def test_hoursverbose(self):
        activate('en')
        self.assertEqual(hoursverbose(60 * 60), '1 hour')
        self.assertEqual(hoursverbose(60 * 60 * 2), '2 hours')
        activate('de')
        self.assertEqual(hoursverbose(60 * 60), '1 Stunde')
        self.assertEqual(hoursverbose(60 * 60 * 2), '2 Stunden')

    # dear future reader, if the HOLIDAYS_PER_MONTH is within some Worker.Contract model, you're welcome :P
    def test_holidays_model(self):
        from systori.apps.timetracking.utils import HOLIDAYS_PER_MONTH as holiday1
        from systori.lib.templatetags.customformatting import HOLIDAYS_PER_MONTH as holiday2
        self.assertEqual(holiday1, holiday2)

    # composed test, this test checks several templatetags which are composed
    def test_dayshoursgainedverbose(self):
        activate('en')
        self.assertEqual(dayshoursgainedverbose(60 * 60 * 1), '2.5 - 0.1 days (20 - 1 hour)')
        self.assertEqual(dayshoursgainedverbose(60*60*8),'2.5 - 1 day (20 - 8 hours)')
        self.assertEqual(dayshoursgainedverbose(60 * 60 * 12), '2.5 - 1.5 days (20 - 12 hours)')
        activate('de')
        self.assertEqual(dayshoursgainedverbose(60 * 60 * 1), '2,5 - 0,1 Tage (20 - 1 Stunde)')
        self.assertEqual(dayshoursgainedverbose(60*60*8),'2,5 - 1 Tag (20 - 8 Stunden)')
        self.assertEqual(dayshoursgainedverbose(60 * 60 * 12), '2,5 - 1,5 Tage (20 - 12 Stunden)')

    def test_zeroblank(self):
        self.assertEqual(zeroblank('0'),'')
        self.assertEqual(zeroblank('23'),'23')

    def test_tosexagesimalhours(self):
        from datetime import time
        self.assertEqual(tosexagesimalhours(60*60*2.5), time(2,30))

    def test_format_seconds(self):
        self.assertEqual(format_seconds(60*60*2.5+60*5), '2:35')
