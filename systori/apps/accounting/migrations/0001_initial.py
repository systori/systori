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
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('account_type', models.CharField(verbose_name='Account Type', choices=[('asset', 'Asset'), ('liability', 'Liability'), ('income', 'Income'), ('expense', 'Expense')], max_length=32)),
                ('code', models.CharField(verbose_name='Code', max_length=32)),
                ('name', models.CharField(verbose_name='Name', blank=True, max_length=512)),
            ],
            options={
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('amount', models.DecimalField(max_digits=14, verbose_name='Amount', default=0.0, decimal_places=4)),
                ('is_payment', models.BooleanField(verbose_name='Payment', default=False)),
                ('received_on', models.DateField(verbose_name='Date Received', default=datetime.date.today)),
                ('is_discount', models.BooleanField(verbose_name='Discount', default=False)),
                ('is_reconciled', models.BooleanField(verbose_name='Reconciled', default=False)),
                ('account', models.ForeignKey(to='accounting.Account', related_name='entries')),
            ],
            options={
                'ordering': ['transaction__recorded_on', 'id'],
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('recorded_on', models.DateTimeField(auto_now_add=True, verbose_name='Date Recorded')),
                ('notes', models.TextField(blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='entry',
            name='transaction',
            field=models.ForeignKey(to='accounting.Transaction', related_name='entries'),
        ),
    ]
