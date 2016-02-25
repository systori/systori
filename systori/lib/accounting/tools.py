from decimal import Decimal
from decimal import ROUND_HALF_UP

# German tax authorities require rounding up from the half cent.
# For example: 0.985 = 0.99
DEFAULT_ROUNDING = ROUND_HALF_UP


def round(num, rounding=DEFAULT_ROUNDING):
    return num.quantize(Decimal('0.01'), rounding=rounding)


def compute_gross_tax(net, tax_rate):
    assert isinstance(net, Decimal)
    assert isinstance(tax_rate, Decimal)

    tax = round(net * tax_rate)

    gross = net + tax

    return gross, tax


def extract_net_tax(gross, tax_rate):
    assert isinstance(gross, Decimal)
    assert isinstance(tax_rate, Decimal)

    inverse_rate = Decimal('1.0') + (Decimal('1.0') / tax_rate)

    tax = round(gross / inverse_rate)

    net = gross - tax

    return net, tax


class Amount:

    @staticmethod
    def zero():
        return Amount(Decimal('0.00'), Decimal('0.00'), Decimal('0.00'))

    @staticmethod
    def from_gross(gross, tax_rate):
        net, tax = extract_net_tax(gross, tax_rate)
        return Amount(net, tax, gross)

    @staticmethod
    def from_net(net, tax_rate):
        gross, tax = compute_gross_tax(net, tax_rate)
        return Amount(net, tax, gross)

    def __init__(self, net, tax, gross):
        assert isinstance(net, Decimal)
        assert isinstance(tax, Decimal)
        assert isinstance(gross, Decimal)
        self.net = net
        self.tax = tax
        self.gross = gross

    def __sub__(self, other):
        assert isinstance(other, Amount)
        return Amount(
                net=self.net-other.net,
                tax=self.tax-other.tax,
                gross=self.gross-other.gross
        )

    def __add__(self, other):
        assert isinstance(other, Amount)
        return Amount(
                net=self.net+other.net,
                tax=self.tax+other.tax,
                gross=self.gross+other.gross
        )
