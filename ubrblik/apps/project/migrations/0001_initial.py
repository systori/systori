# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(verbose_name='Project Name', max_length=512)),
                ('description', models.TextField(null=True, blank=True, verbose_name='Project Description')),
                ('is_template', models.BooleanField(default=False)),
                ('job_zfill', models.PositiveSmallIntegerField(default=1, verbose_name='Job Code Zero Fill')),
                ('taskgroup_zfill', models.PositiveSmallIntegerField(default=1, verbose_name='Task Group Code Zero Fill')),
                ('task_zfill', models.PositiveSmallIntegerField(default=1, verbose_name='Task Code Zero Fill')),
            ],
            options={
                'verbose_name_plural': 'Projects',
                'ordering': ['name'],
                'verbose_name': 'Project',
            },
            bases=(models.Model,),
        ),
    ]
