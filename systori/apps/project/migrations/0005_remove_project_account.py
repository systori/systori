# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.utils.translation import activate


def convert_project_account_to_job_account(apps, schema_editor):
    activate('en')
    from systori.apps.company.models import Company
    from scripts.account_analyzer import migrate_accounts
    for company in Company.objects.all():
        company.activate()
        print("\n\n=== Company: {} ===\n\n".format(company.name))
        migrate_accounts(company)


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0004_remove_project_job_offset'),
        ('task', '0005_job_account'),
        ('accounting', '0005_entry_job')
    ]

    operations = [
        migrations.RunPython(convert_project_account_to_job_account),
#        migrations.RemoveField(
#            model_name='project',
#            name='account',
#        ),
    ]
