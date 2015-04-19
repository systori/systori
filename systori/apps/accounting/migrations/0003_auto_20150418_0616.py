# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.datetime_safe
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0002_auto_20150416_0412'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='project',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='transaction_group',
        ),
        migrations.DeleteModel(
            name='Payment',
        ),
        migrations.AlterModelOptions(
            name='account',
            options={'ordering': ['code']},
        ),
        migrations.RemoveField(
            model_name='entry',
            name='is_adjustment',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='group',
        ),
        migrations.DeleteModel(
            name='TransactionGroup',
        ),
        migrations.AddField(
            model_name='account',
            name='name',
            field=models.CharField(max_length=512, verbose_name='Name', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entry',
            name='is_payment',
            field=models.BooleanField(default=False, verbose_name='Payment'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entry',
            name='received_on',
            field=models.DateField(default=datetime.date.today, verbose_name='Date Received'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='transaction',
            name='notes',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='transaction',
            name='recorded_on',
            field=models.DateTimeField(default=django.utils.datetime_safe.date.today, verbose_name='Date Recorded', auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='account',
            name='account_type',
            field=models.CharField(choices=[('asset', 'Asset'), ('liability', 'Liability'), ('income', 'Income'), ('expense', 'Expense')], max_length=32, verbose_name='Account Type'),
            preserve_default=True,
        ),
    ]
