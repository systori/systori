# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0001_initial'),
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyplan',
            name='tasks',
            field=models.ManyToManyField(to='task.Task', related_name='dailyplans'),
        ),
    ]
