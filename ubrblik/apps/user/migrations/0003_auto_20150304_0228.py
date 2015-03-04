# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20150304_0219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_laborer',
            field=models.BooleanField(verbose_name='Laborer', help_text='Laborer has limited access to the system.', default=True),
            preserve_default=True,
        ),
    ]
