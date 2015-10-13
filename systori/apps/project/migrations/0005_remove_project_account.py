# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from systori.apps.accounting.models import create_account_for_job
from django.utils.translation import activate


def convert_project_account_to_job_account(apps, schema_editor):

    activate('en')

    from systori.apps.project.models import Project
    from systori.apps.company.models import Company
    from scripts.account_analyzer import migrate_accounts

    OldProject = apps.get_model('project', 'Project')

    for company in Company.objects.all():
        company.activate()
        migrate_accounts()


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0004_remove_project_job_offset'),
        ('task', '0005_job_account'),
        ('accounting', '0004_auto_20151013_0730')
    ]

    operations = [
        migrations.RunPython(convert_project_account_to_job_account),
#        migrations.RemoveField(
#            model_name='project',
#            name='account',
#        ),
    ]
