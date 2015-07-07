# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0002_auto_20150706_0557'),
        ('task', '0001_initial'),
    ]

    operations = [
        # Add a nullable access field, convert user id's to access id's, then
        # set the column as non-null and finally delete the old user column
        migrations.AddField(
            model_name='progressreport',
            name='access',
            field=models.ForeignKey(to='company.Access', null=True, related_name='filedreports')
        ),
        migrations.RunSQL(
            "UPDATE task_progressreport tbl SET access_id = ca.id FROM company_access ca WHERE ca.user_id=tbl.user_id AND ca.company_id='mehr_handwerk'"
        ),
        migrations.AlterField(
            model_name='progressreport',
            name='access',
            field=models.ForeignKey(related_name='filedreports', to='company.Access'),
        ),
        migrations.RemoveField(
            model_name='progressreport',
            name='user',
        ),
    ]
