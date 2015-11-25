# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations
from decimal import Decimal


def is_bank(account):
    if account.code.isdigit():
        code = int(account.code)
        if 1200 <= code <= 1288:
            return True
    return False


def set_missing_values(apps, schema_editor):
    Account = apps.get_model('accounting', 'Account')
    Entry = apps.get_model('accounting', 'Entry')
    from systori.apps.company.models import Company
    for company in Company.objects.all():
        company.activate()
        for asset in Account.objects.filter(account_type='asset'):
            asset.asset_type = 'bank' if is_bank(asset) else 'receivable'
            asset.save()
        for entry in Entry.objects.all():
            if entry.entry_type in ("payment", "work-debit", "flat-debit"):
                entry.rate = Decimal('0.19')
                entry.save()
            if entry.entry_type == "final-debit":
                entry.entry_type = 'work-debit'
                entry.save()


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0005_entry_job'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='rate',
            field=models.DecimalField(decimal_places=2, max_digits=14, default=0, verbose_name='Rate'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=14, verbose_name='Amount'),
        ),
        migrations.AddField(
            model_name='account',
            name='asset_type',
            field=models.CharField(max_length=32, choices=[('bank', 'Bank'), ('receivable', 'Accounts Receivable')], verbose_name='Asset Type', null=True),
        ),
        migrations.AlterField(
            model_name='entry',
            name='entry_type',
            field=models.CharField(verbose_name='Entry Type', choices=[('payment', 'Payment'), ('discount', 'Discount'), ('work-debit', 'Work Debit'), ('flat-debit', 'Flat Debit'), ('adjustment', 'Adjustment'), ('other', 'Other')], default='other', max_length=32),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(max_length=32, choices=[('invoice', 'Invoice'), ('final-invoice', 'Final Invoice'), ('payment', 'Payment'), ('adjustment', 'Adjustment')], verbose_name='Transaction Type', null=True),
        ),
        migrations.RunPython(set_missing_values),
    ]
