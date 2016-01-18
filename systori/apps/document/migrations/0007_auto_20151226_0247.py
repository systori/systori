# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0006_auto_20151119_2148'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='json_version',
        ),
        migrations.RemoveField(
            model_name='proposal',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='proposal',
            name='json_version',
        ),
    ]
