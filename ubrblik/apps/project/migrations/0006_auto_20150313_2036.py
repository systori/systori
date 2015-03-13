# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0005_auto_20150312_1901'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dailyplan',
            options={'ordering': ['day']},
        ),
        migrations.RenameField(
            model_name='dailyplan',
            old_name='site',
            new_name='jobsite',
        ),
    ]
