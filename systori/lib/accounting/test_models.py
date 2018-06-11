from decimal import Decimal as D
from django.test import TestCase
from django.db import connection
from .models import *


class Account(BaseAccount):
    _is_shared_model = True
    pass


class Entry(BaseEntry):
    _is_shared_model = True
    pass


class Transaction(BaseTransaction):
    _is_shared_model = True
    entry_class = Entry
    account_class = Account


class AccountingTestCase(TestCase):

    CONCRETE_MODELS = [Account, Entry, Transaction]

    def setUp(self):
        super().setUp()
        schema_editor = connection.schema_editor()
        schema_editor.deferred_sql = []
        for model in self.CONCRETE_MODELS:
            schema_editor.create_model(model)


class EntryTests(AccountingTestCase):
    def test_net_value(self):
        a = Entry(value=D("99.00"), value_type=Entry.NET).amount
        self.assertIsInstance(a, Amount)
        self.assertEqual(D("99.00"), a.net)
        self.assertEqual(D("0.00"), a.tax)
        self.assertEqual(D("99.00"), a.gross)

    def test_tax_value(self):
        a = Entry(value=D("99.00"), value_type=Entry.TAX).amount
        self.assertIsInstance(a, Amount)
        self.assertEqual(D("0.00"), a.net)
        self.assertEqual(D("99.00"), a.tax)
        self.assertEqual(D("99.00"), a.gross)

    def test_gross_value(self):
        a = Entry(value=D("99.00"), value_type=Entry.GROSS).amount
        self.assertIsInstance(a, Amount)
        self.assertEqual(D("0.00"), a.net)
        self.assertEqual(D("0.00"), a.tax)
        self.assertEqual(D("99.00"), a.gross)

    def test_sum_entries(self):
        a = Account.objects.create()
        t = Transaction.objects.create()
        Entry.objects.create(
            value=D("10.00"), value_type=Entry.TAX, transaction=t, account=a
        )
        Entry.objects.create(
            value=D("30.00"), value_type=Entry.NET, transaction=t, account=a
        )
        sum = Entry.objects.all().sum
        self.assertEqual(D("30.00"), sum.net)
        self.assertEqual(D("10.00"), sum.tax)
        self.assertEqual(D("40.00"), sum.gross)
