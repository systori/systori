# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0006_auto_20150321_0314'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyplan',
            name='notes',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
