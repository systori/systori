from decimal import Decimal
from decimal import ROUND_HALF_UP

# German tax authorities require rounding up from the half cent.
# For example: 0.985 = 0.99
DEFAULT_ROUNDING = ROUND_HALF_UP


def compute_gross_tax(net, tax_rate, rounding=DEFAULT_ROUNDING):
    assert isinstance(net, Decimal)
    assert isinstance(tax_rate, Decimal)

    tax = (net * tax_rate).quantize(Decimal('0.01'), rounding=rounding)

    gross = net + tax

    return gross, tax


def extract_net_tax(gross, tax_rate, rounding=DEFAULT_ROUNDING):
    assert isinstance(gross, Decimal)
    assert isinstance(tax_rate, Decimal)

    inverse_rate = Decimal('1.0') + (Decimal('1.0') / tax_rate)

    tax = (gross / inverse_rate).quantize(Decimal('0.01'), rounding=rounding)

    net = gross - tax

    return net, tax
