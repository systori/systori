# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0002_job_taskgroup_offset'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='task',
            options={'verbose_name': 'Task', 'verbose_name_plural': 'Task', 'ordering': ['order']},
        ),
        migrations.AlterModelOptions(
            name='taskgroup',
            options={'verbose_name': 'Task Group', 'verbose_name_plural': 'Task Groups', 'ordering': ['order']},
        ),
        migrations.AlterModelOptions(
            name='taskinstance',
            options={'verbose_name': 'Task Instance', 'verbose_name_plural': 'Task Instances', 'ordering': ['order']},
        ),
    ]
