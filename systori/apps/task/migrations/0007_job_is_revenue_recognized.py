# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0006_task_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='is_revenue_recognized',
            field=models.BooleanField(default=False),
        ),
    ]
