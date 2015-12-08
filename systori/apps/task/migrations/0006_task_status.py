# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0005_job_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='status',
            field=django_fsm.FSMField(choices=[('approved', 'Approved'), ('ready', 'Ready'), ('running', 'Running'), ('done', 'Done')], blank=True, max_length=50),
        ),
    ]
