from decimal import Decimal
from decimal import ROUND_HALF_UP
from jsonfield.encoder import JSONEncoder as BaseJSONEncoder


# German tax authorities require rounding up from the half cent.
# For example: 0.985 = 0.99
DEFAULT_ROUNDING = ROUND_HALF_UP


def round(num, rounding=DEFAULT_ROUNDING):
    return num.quantize(Decimal("0.01"), rounding=rounding)


def compute_gross_tax(net, tax_rate):
    assert isinstance(net, Decimal)
    assert isinstance(tax_rate, Decimal)

    tax = round(net * tax_rate)

    gross = net + tax

    return gross, tax


def extract_net_tax(gross, tax_rate):
    assert isinstance(gross, Decimal)
    assert isinstance(tax_rate, Decimal)

    inverse_rate = Decimal("1.0") + (Decimal("1.0") / tax_rate)

    tax = round(gross / inverse_rate)

    net = gross - tax

    return net, tax


class Amount:
    @staticmethod
    def zero():
        return Amount(Decimal("0.00"), Decimal("0.00"), Decimal("0.00"))

    @staticmethod
    def from_gross(gross, tax_rate):
        net, tax = extract_net_tax(gross, tax_rate)
        return Amount(net, tax, gross)

    @staticmethod
    def from_net(net, tax_rate):
        gross, tax = compute_gross_tax(net, tax_rate)
        return Amount(net, tax, gross)

    @staticmethod
    def from_entry(entry):
        return Amount(
            net=entry.value if entry.is_net else Decimal("0.00"),
            tax=entry.value if entry.is_tax else Decimal("0.00"),
            gross=entry.value if entry.is_gross else None,
        )

    def __init__(self, net, tax, gross=None):
        assert isinstance(net, Decimal)
        assert isinstance(tax, Decimal)
        assert gross is None or isinstance(gross, Decimal)
        self.net = net
        self.tax = tax
        self.gross = gross
        self.gross_was_calculated = False
        if gross is None:
            self.gross = self.net + self.tax
            self.gross_was_calculated = True

    @property
    def negate(self):
        return Amount(net=self.net * -1, tax=self.tax * -1, gross=self.gross * -1)

    @property
    def net_amount(self):
        return Amount(net=self.net, tax=Decimal(0), gross=self.net)

    @property
    def tax_amount(self):
        return Amount(net=Decimal(0), tax=self.tax, gross=self.tax)

    def __sub__(self, other):
        assert isinstance(other, Amount)
        return Amount(
            net=self.net - other.net,
            tax=self.tax - other.tax,
            gross=self.gross - other.gross,
        )

    def __add__(self, other):
        assert isinstance(other, Amount)
        return Amount(
            net=self.net + other.net,
            tax=self.tax + other.tax,
            gross=self.gross + other.gross,
        )

    def __eq__(self, other):
        if other is None:
            return False
        return (
            self.net == other.net
            and self.tax == other.tax
            and self.gross == other.gross
        )

    def __repr__(self):
        return "Amount(net=%s, tax=%s, gross=%s)" % (self.net, self.tax, self.gross)

    # JSON Serialization & Deserialization

    @property
    def to_json(self):
        return {"_amount_": {"net": self.net, "tax": self.tax, "gross": self.gross}}

    @staticmethod
    def object_hook(value):
        if "_amount_" in value:
            return Amount(**value["_amount_"])
        return value


class JSONEncoder(BaseJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Amount):
            return obj.to_json
        return super().default(obj)
