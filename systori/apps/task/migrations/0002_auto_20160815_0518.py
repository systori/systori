# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-15 03:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='progressreport',
            old_name='access',
            new_name='worker',
        ),
    ]
