# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0006_auto_20150313_2036'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dailyplan',
            options={'ordering': ['-day']},
        ),
        migrations.AlterModelOptions(
            name='teammember',
            options={'ordering': ['-is_foreman', 'member__first_name']},
        ),
    ]
