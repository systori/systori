# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-19 20:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0002_auto_20160221_0254'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='first_name',
            field=models.CharField(blank=True, max_length=512, verbose_name='First Name'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='last_name',
            field=models.CharField(blank=True, max_length=512, verbose_name='Last Name'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='phone',
            field=models.CharField(blank=True, max_length=512, verbose_name='Phone'),
        ),
    ]