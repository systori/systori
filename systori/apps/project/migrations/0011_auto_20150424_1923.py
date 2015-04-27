# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0010_auto_20150422_0248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='state',
            field=django_fsm.FSMField(choices=[('active', 'Active'), ('paused', 'Paused'), ('disputed', 'Disputed'), ('stopped', 'Stopped')], max_length=50, default='active'),
        ),
    ]
