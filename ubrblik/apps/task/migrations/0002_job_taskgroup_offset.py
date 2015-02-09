# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='taskgroup_offset',
            field=models.PositiveSmallIntegerField(verbose_name='Task Group Offset', default=0),
            preserve_default=True,
        ),
    ]
