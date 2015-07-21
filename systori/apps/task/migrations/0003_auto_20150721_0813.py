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
                job.code = str(job.order + 1 + project.job_offset).zfill(project.job_zfill)
                job.save()
                for taskgroup in job.taskgroups.all():
                    taskgroup.code = str(taskgroup.order + 1 + job.taskgroup_offset).zfill(project.taskgroup_zfill)
                    taskgroup.save()
                    for task in taskgroup.tasks.all():
                        task.code = str(task.order + 1).zfill(project.task_zfill)
                        task.save()


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0002_auto_20150707_0627'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='code',
            field=models.CharField(default=1, verbose_name='Code', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='task',
            name='code',
            field=models.CharField(default=1, verbose_name='Code', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='taskgroup',
            name='code',
            field=models.CharField(default=1, verbose_name='Code', max_length=128),
            preserve_default=False,
        ),
        migrations.RunPython(update_code)
    ]
