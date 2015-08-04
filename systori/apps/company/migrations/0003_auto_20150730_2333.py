# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0002_auto_20150706_0557'),
    ]

    operations = [
        migrations.AlterField(
            model_name='access',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='active', help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts. This will remove user from any present and future daily plans.'),
        ),
    ]
