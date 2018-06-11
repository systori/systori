import json
from decimal import Decimal as D
from django.test import TestCase
from .tools import *


class GrossNetConversionTest(TestCase):
    def test_our_favorite_examples(self):

        self.assertEqual(
            (D("1190.00"), D("190.00")), compute_gross_tax(D("1000.00"), D("0.19"))
        )
        self.assertEqual(
            (D("1000.00"), D("190.00")), extract_net_tax(D("1190.00"), D("0.19"))
        )

        self.assertEqual(
            (D("1189.99"), D("190.00")), compute_gross_tax(D("999.99"), D("0.19"))
        )
        self.assertEqual(
            (D("999.99"), D("190.00")), extract_net_tax(D("1189.99"), D("0.19"))
        )

    def test_brute_force_reversibility_from_one_penny_to_a_thousand(self):
        """
        Job/Receivables accounting is done with gross amounts but we want to be able to
        display net and tax amounts everywhere, so it's really important that we can
        reliably and consistently convert between: (net, tax) -> gross -> (net, tax).
        This test basically tests every number between 0.01 and 1,000.00
        It's stupid but it makes it easier to sleep at night :-D
        """
        tax_rate = D(".19")
        original_net = Decimal("0.00")
        for i in range(100000):
            original_net += Decimal(".01")
            gross, gross_tax = compute_gross_tax(original_net, tax_rate)
            extracted_net, net_tax = extract_net_tax(gross, tax_rate)
            self.assertEqual(original_net, extracted_net)
            self.assertEqual(gross_tax, net_tax)


class AmountTests(TestCase):
    def test_default_init(self):
        a = Amount(D(1), D(2), D(3))
        self.assertEqual(a.net, D(1))
        self.assertEqual(a.tax, D(2))
        self.assertEqual(a.gross, D(3))
        self.assertFalse(a.gross_was_calculated)

    def test_gross_calculated(self):
        a = Amount(D(3), D(2))
        self.assertEqual(a.gross, D(5))
        self.assertTrue(a.gross_was_calculated)

    def test_zero_init(self):
        a = Amount.zero()
        self.assertEqual(a.net, D(0))
        self.assertEqual(a.tax, D(0))
        self.assertEqual(a.gross, D(0))

    def test_from_net_init(self):
        a = Amount.from_net(D(100), D(0.19))
        self.assertEqual(a.net, D(100))
        self.assertEqual(a.tax, D(19))
        self.assertEqual(a.gross, D(119))

    def test_from_gross_init(self):
        a = Amount.from_gross(D(119), D(0.19))
        self.assertEqual(a.net, D(100))
        self.assertEqual(a.tax, D(19))
        self.assertEqual(a.gross, D(119))

    def test_ops(self):
        a = Amount(D(1), D(2), D(3))

        a += a
        self.assertEqual(a.net, D(2))
        self.assertEqual(a.tax, D(4))
        self.assertEqual(a.gross, D(6))

        a -= Amount(D(1), D(1), D(1))
        self.assertEqual(a.net, D(1))
        self.assertEqual(a.tax, D(3))
        self.assertEqual(a.gross, D(5))


class AmountJSONTests(TestCase):
    def test_serialize(self):
        invoiced = {"invoiced": Amount(D(1000), D(190))}
        j = json.dumps(invoiced, cls=JSONEncoder)
        l = json.loads(j)
        self.assertEquals(
            {"invoiced": {"_amount_": {"tax": 190.0, "net": 1000.0, "gross": 1190.0}}},
            l,
        )

    def test_deserialize(self):
        l = json.loads(
            '{"invoiced": {"_amount_": {"tax": 190.0, "net": 1000.0, "gross": 1190.0}}}',
            object_hook=Amount.object_hook,
            parse_float=Decimal,
        )
        self.assertIsInstance(l["invoiced"], Amount)
        self.assertEqual(D(190), l["invoiced"].tax)
        self.assertEqual(D(1000), l["invoiced"].net)
        self.assertEqual(D(1190), l["invoiced"].gross)

    def test_round_trip(self):
        invoiced = {"invoiced": Amount(D(1000), D(190))}
        j = json.dumps(invoiced, cls=JSONEncoder)
        l = json.loads(j, object_hook=Amount.object_hook, parse_float=Decimal)
        self.assertIsInstance(l["invoiced"], Amount)
        self.assertEqual(D(190), l["invoiced"].tax)
        self.assertEqual(D(1000), l["invoiced"].net)
        self.assertEqual(D(1190), l["invoiced"].gross)
