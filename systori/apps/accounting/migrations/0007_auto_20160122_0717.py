# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0006_auto_20151124_2102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='entry_type',
            field=models.CharField(choices=[('payment', 'Payment'), ('discount', 'Discount'), ('work-debit', 'Work Debit'), ('flat-debit', 'Flat Debit'), ('refund-debit', 'Refund Debit'), ('adjustment', 'Adjustment'), ('other', 'Other')], max_length=32, verbose_name='Entry Type', default='other'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(choices=[('invoice', 'Invoice'), ('payment', 'Payment'), ('adjustment', 'Adjustment'), ('refund', 'Refund')], max_length=32, verbose_name='Transaction Type', null=True),
        ),
    ]
