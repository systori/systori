# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0003_auto_20151013_0615'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entry',
            name='is_discount',
        ),
        migrations.RemoveField(
            model_name='entry',
            name='is_payment',
        ),
        migrations.RemoveField(
            model_name='entry',
            name='received_on',
        ),
    ]
