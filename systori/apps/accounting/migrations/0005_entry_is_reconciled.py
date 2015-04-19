# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0004_auto_20150418_0732'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='is_reconciled',
            field=models.BooleanField(verbose_name='Reconciled', default=False),
            preserve_default=True,
        ),
    ]
