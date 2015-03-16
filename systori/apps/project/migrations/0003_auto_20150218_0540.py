# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0002_project_job_offset'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='address',
            field=models.CharField(verbose_name='Address', max_length=512, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='city',
            field=models.CharField(verbose_name='City', max_length=512, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='country',
            field=models.CharField(verbose_name='Country', max_length=512, default='Deutschland'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='latitude',
            field=models.FloatField(null=True, blank=True, verbose_name='Latitude'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='longitude',
            field=models.FloatField(null=True, blank=True, verbose_name='Longitude'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='postal_code',
            field=models.CharField(verbose_name='Postal Code', max_length=512, default=''),
            preserve_default=False,
        ),
    ]
