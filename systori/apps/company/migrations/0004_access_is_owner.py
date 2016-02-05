# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0003_auto_20150730_2333'),
    ]

    operations = [
        migrations.AddField(
            model_name='access',
            name='is_owner',
            field=models.BooleanField(verbose_name='Owner', default=False, help_text='Owner has full and unlimited Access to Systori.'),
        ),
    ]
