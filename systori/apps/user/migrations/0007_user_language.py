# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_auto_20150706_0600'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='language',
            field=models.CharField(blank=True, verbose_name='language', max_length=2, choices=[('de', 'Deutsch'), ('en', 'English')]),
        ),
    ]
