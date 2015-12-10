# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations
from decimal import Decimal
from systori.lib.accounting.tools import extract_net_tax


def is_bank(account):
    if account.code.isdigit():
        code = int(account.code)
        if 1200 <= code <= 1288:
            return True
    return False


def set_missing_values(apps, schema_editor):
    from systori.apps.company.models import Company
    Account = apps.get_model('accounting', 'Account')
    Entry = apps.get_model('accounting', 'Entry')
    Invoice = apps.get_model('document', 'Invoice')

    for company in Company.objects.all():
        company.activate()

        for asset in Account.objects.filter(account_type='asset'):
            asset.asset_type = 'bank' if is_bank(asset) else 'receivable'
            asset.save()

        for entry in Entry.objects.all():
            if entry.entry_type != "other":
                if entry.entry_type == "final-debit":
                    entry.entry_type = "work-debit"
                entry.tax_rate = Decimal('0.19')
                entry.save()

        for invoice in Invoice.objects.all():
            for job in invoice.json.get('debits', []):
                job['amount_net'] = job['debit_net']
                job['amount_gross'] = job['debit_amount']
                job['amount_tax'] = job['debit_tax']
                job['is_override'] = job['is_flat']
                job['override_comment'] = job['debit_comment']
                job['debited_gross'] = job['debited']
                job['debited_net'], job['debited_tax'] = extract_net_tax(Decimal(job['debited']), Decimal('0.19'))
                job['balance_gross'] = job['balance']
                job['balance_net'], job['balance_tax'] = extract_net_tax(Decimal(job['balance']), Decimal('0.19'))
                job['estimate_net'] = extract_net_tax(Decimal(job['estimate']), Decimal('0.19'))[0]
                job['itemized_net'] = extract_net_tax(Decimal(job['itemized']), Decimal('0.19'))[0]
            invoice.save()


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0005_entry_job'),
        ('document', '0006_auto_20151119_2148'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='tax_rate',
            field=models.DecimalField(decimal_places=2, max_digits=14, default=0, verbose_name='Tax Rate'),
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
        migrations.AddField(
            model_name='transaction',
            name='is_revenue_recognized',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(set_missing_values),
    ]
