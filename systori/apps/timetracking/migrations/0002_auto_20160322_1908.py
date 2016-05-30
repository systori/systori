# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timetracking', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timer',
            name='start',
            field=models.DateTimeField(db_index=True),
        ),
    ]
