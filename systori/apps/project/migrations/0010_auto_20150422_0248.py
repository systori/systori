# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0009_project_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='phase',
            field=django_fsm.FSMField(max_length=50, choices=[('prospective', 'Prospective'), ('tendering', 'Tendering'), ('planning', 'Planning'), ('executing', 'Executing'), ('settlement', 'Settlement'), ('warranty', 'Warranty'), ('finished', 'Finished')], default='prospective'),
        ),
        migrations.AddField(
            model_name='project',
            name='state',
            field=django_fsm.FSMField(max_length=50, choices=[('active', 'Active'), ('paused', 'Paused'), ('canceled', 'Canceled'), ('disputed', 'Disputed'), ('stopped', 'Stopped')], default='active'),
        ),
    ]
