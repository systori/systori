# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0004_auto_20150311_1705'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobsite',
            name='name',
            field=models.CharField(blank=True, verbose_name='Site Name', max_length=512),
            preserve_default=True,
        ),
    ]
