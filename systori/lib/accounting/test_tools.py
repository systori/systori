from decimal import Decimal as D
from django.test import TestCase
from .tools import *


class GrossNetConversionTest(TestCase):

    def test_our_favorite_examples(self):

        self.assertEqual((D('1190.00'), D('190.00')), compute_gross_tax(D('1000.00'), D('0.19')))
        self.assertEqual((D('1000.00'), D('190.00')), extract_net_tax(D('1190.00'), D('0.19')))

        self.assertEqual((D('1189.99'), D('190.00')), compute_gross_tax(D('999.99'), D('0.19')))
        self.assertEqual((D('999.99'), D('190.00')), extract_net_tax(D('1189.99'), D('0.19')))

    def test_brute_force_reversibility_from_one_penny_to_a_thousand(self):
        """
        Job/Receivables accounting is done with gross amounts but we want to be able to
        display net and tax amounts everywhere, so it's really important that we can
        reliably and consistently convert between: (net, tax) -> gross -> (net, tax).
        This test basically tests every number between 0.01 and 1,000.00
        It's stupid but it makes it easier to sleep at night :-D
        """
        tax_rate = D('.19')
        original_net = Decimal('0.00')
        for i in range(100000):
            original_net += Decimal('.01')
            gross, gross_tax = compute_gross_tax(original_net, tax_rate)
            extracted_net, net_tax = extract_net_tax(gross, tax_rate)
            self.assertEqual(original_net, extracted_net)
            self.assertEqual(gross_tax, net_tax)
