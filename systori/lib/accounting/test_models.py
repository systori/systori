from decimal import Decimal as D
from django.test import TestCase
from django.db import connection
from django.core.management.color import no_style
from .models import *


class Account(BaseAccount):
    pass


class Entry(BaseEntry):
    pass


class Transaction(BaseTransaction):
    entry_class = Entry
    account_class = Account


class AccountingTestCase(TestCase):

    CONCRETE_MODELS = [Account, Entry, Transaction]

    def setUp(self):
        super().setUp()
        pending_references = {}
        tables = connection.introspection.table_names()
        known_models = connection.introspection.installed_models(tables)
        cursor = connection.cursor()
        for model in self.CONCRETE_MODELS:
            sql, references = connection.creation.sql_create_model(model, no_style(), known_models)
            for refto, refs in references.items():
                pending_references.setdefault(refto, []).extend(refs)
                if refto in known_models:
                    sql.extend(connection.creation.sql_for_pending_references(refto, no_style(), pending_references))
            sql.extend(connection.creation.sql_for_pending_references(model, no_style(), pending_references))
            for statement in sql:
                cursor.execute(statement)
            known_models.add(model)


class EntryTests(AccountingTestCase):
    def test_net_value(self):
        a = Entry(value=D('99.00'), value_type=Entry.NET).amount
        self.assertIsInstance(a, Amount)
        self.assertEqual(D('99.00'), a.net)
        self.assertEqual(D('0.00'), a.tax)
        self.assertEqual(D('99.00'), a.gross)

    def test_tax_value(self):
        a = Entry(value=D('99.00'), value_type=Entry.TAX).amount
        self.assertIsInstance(a, Amount)
        self.assertEqual(D('0.00'), a.net)
        self.assertEqual(D('99.00'), a.tax)
        self.assertEqual(D('99.00'), a.gross)

    def test_gross_value(self):
        a = Entry(value=D('99.00'), value_type=Entry.GROSS).amount
        self.assertIsInstance(a, Amount)
        self.assertEqual(D('0.00'), a.net)
        self.assertEqual(D('0.00'), a.tax)
        self.assertEqual(D('99.00'), a.gross)

    def test_sum_entries(self):
        a = Account.objects.create()
        t = Transaction.objects.create()
        Entry.objects.create(value=D('10.00'), value_type=Entry.TAX, transaction=t, account=a)
        Entry.objects.create(value=D('30.00'), value_type=Entry.NET, transaction=t, account=a)
        sum = Entry.objects.all().sum
        self.assertEqual(D('30.00'), sum.net)
        self.assertEqual(D('10.00'), sum.tax)
        self.assertEqual(D('40.00'), sum.gross)
