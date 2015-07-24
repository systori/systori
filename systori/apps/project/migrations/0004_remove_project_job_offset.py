# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0003_auto_20150707_0627'),
        ('task', '0003_auto_20150721_0813'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='job_offset',
        ),
    ]
