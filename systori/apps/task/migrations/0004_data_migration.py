# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def copy_old_job_to_new_job(apps, schema_editor):
    from systori.apps.company.models import Company
    Job = apps.get_model("task", "Job")
    OldJob = apps.get_model("task", "OldJob")
    Group = apps.get_model("task", "Group")
    TOKEN = 0
    for company in Company.objects.all():
        company.activate()

        schema_editor.execute(
            "select setval(pg_get_serial_sequence('task_group', 'id'), max(id)) from task_oldjob;"
        )

        for old_job in OldJob.objects.all():

            TOKEN += 1
            job = Job.objects.create(
                id=old_job.id,
                token=TOKEN,
                order=old_job.job_code,
                name=old_job.name,
                description=old_job.description,
                billing_method=old_job.billing_method,
                is_revenue_recognized=old_job.is_revenue_recognized,
                status=old_job.status,
                account=old_job.account,
                project=old_job.project
            )
            job.job = job
            job.save()

            for taskgroup in old_job.taskgroups.all():
                TOKEN += 1
                group = Group.objects.create(
                    parent=job,
                    job=job,
                    token=TOKEN,
                    name=taskgroup.name,
                    description=taskgroup.description,
                    order=taskgroup.order + 1 + old_job.taskgroup_offset
                )
                for task in taskgroup.tasks.all():
                    TOKEN += 1
                    task.token = TOKEN
                    task.job = job
                    task.group = group
                    task.save()


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0003_group_refactor'),
    ]

    operations = [
        migrations.RunPython(copy_old_job_to_new_job),
    ]
