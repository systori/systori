# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0009_letterhead_bottom_margin_next'),
    ]

    operations = [
        migrations.AddField(
            model_name='letterhead',
            name='stylesheet',
            field=models.CharField(default='OpenSans', max_length=15, choices=[('OpenSans', 'Open Sans'), ('droid-serif', 'Droid Serif'), ('tinos', 'Tinos')], verbose_name='Font type'),
        ),
    ]
