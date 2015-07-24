# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from string import ascii_lowercase


def update_code(apps, schema_editor):
    Project = apps.get_model('project', 'Project')
    from systori.apps.company.models import Company
    for company in Company.objects.all():
        company.activate()
        for project in Project.objects.all():
            for job in project.jobs.all():
                job.job_code = str(job.order + 1 + project.job_offset).zfill(project.job_zfill)
                job.save()


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0002_auto_20150707_0627'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='job_code',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Code'),
            preserve_default=True,
        ),
        migrations.RunPython(update_code),
    ]
