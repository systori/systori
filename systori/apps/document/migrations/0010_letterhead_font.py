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
            name='font',
            field=models.CharField(verbose_name='Font type', choices=[('OpenSans', 'Open Sans'), ('DroidSerif', 'Droid Serif'), ('Tinos', 'Tinos')], default='OpenSans', max_length=15),
        ),
    ]
