# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('account_type', models.CharField(max_length=32, choices=[('asset', 'Asset'), ('liability', 'Liability'), ('income', 'Income'), ('expense', 'Expense')], verbose_name='Account Type')),
                ('asset_type', models.CharField(max_length=32, null=True, choices=[('bank', 'Bank'), ('receivable', 'Accounts Receivable')], verbose_name='Asset Type')),
                ('code', models.CharField(max_length=32, verbose_name='Code')),
                ('name', models.CharField(max_length=512, verbose_name='Name', blank=True)),
            ],
            options={
                'ordering': ['code'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('amount', models.DecimalField(max_digits=14, verbose_name='Amount', decimal_places=2)),
                ('tax_rate', models.DecimalField(max_digits=14, default=0, verbose_name='Tax Rate', decimal_places=2)),
                ('entry_type', models.CharField(max_length=32, default='other', choices=[('payment', 'Payment'), ('refund-credit', 'Refund Credit'), ('discount', 'Discount'), ('work-debit', 'Work Debit'), ('flat-debit', 'Flat Debit'), ('refund-debit', 'Refund Debit'), ('adjustment', 'Adjustment'), ('other', 'Other')], verbose_name='Entry Type')),
                ('reconciled_on', models.DateField(null=True, verbose_name='Date Reconciled')),
                ('is_reconciled', models.BooleanField(default=False, verbose_name='Reconciled')),
                ('account', models.ForeignKey(to='accounting.Account', related_name='entries')),
            ],
            options={
                'ordering': ['transaction__transacted_on', 'id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('notes', models.TextField(blank=True)),
                ('transacted_on', models.DateField(default=datetime.date.today, verbose_name='Date Transacted')),
                ('finalized_on', models.DateField(null=True, verbose_name='Date Finalized')),
                ('is_finalized', models.BooleanField(default=False, verbose_name='Finalized')),
                ('is_revenue_recognized', models.BooleanField(default=False)),
                ('recorded_on', models.DateTimeField(auto_now_add=True, verbose_name='Date Recorded')),
                ('transaction_type', models.CharField(max_length=32, null=True, choices=[('invoice', 'Invoice'), ('payment', 'Payment'), ('adjustment', 'Adjustment'), ('refund', 'Refund')], verbose_name='Transaction Type')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
