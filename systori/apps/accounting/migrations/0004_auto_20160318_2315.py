# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0003_added_value_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(max_length=32, verbose_name='Transaction Type', null=True, choices=[('invoice', 'Invoice'), ('payment', 'Payment'), ('adjustment', 'Adjustment'), ('refund', 'Refund')]),
        ),
    ]
