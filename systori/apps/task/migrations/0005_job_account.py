# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0003_auto_20151030_1121'),
        ('accounting', '0002_auto_20150730_0445'),
        ('task', '0004_auto_20150724_0617'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='account',
            field=models.OneToOneField(to='accounting.Account', related_name='job', null=True, on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
