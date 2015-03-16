# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_foreman',
            field=models.BooleanField(help_text='Foremen can manage laborers.', verbose_name='Foreman', default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='is_laborer',
            field=models.BooleanField(help_text='Laborer has limited access to the system.', verbose_name='Laborer', default=False),
            preserve_default=True,
        ),
    ]
