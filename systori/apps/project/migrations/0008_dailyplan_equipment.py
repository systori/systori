# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '__first__'),
        ('project', '0007_dailyplan_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyplan',
            name='equipment',
            field=models.ManyToManyField(related_name='dailyplans', to='equipment.Equipment'),
            preserve_default=True,
        ),
    ]
