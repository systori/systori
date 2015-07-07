# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0002_auto_20150706_0557'),
        ('project', '0002_auto_20150615_0046'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='teammember',
            options={'ordering': ['-is_foreman', 'access__user__first_name']},
        ),
        migrations.RemoveField(
            model_name='dailyplan',
            name='users',
        ),
        migrations.AddField(
            model_name='dailyplan',
            name='accesses',
            field=models.ManyToManyField(to='company.Access', through='project.TeamMember', related_name='dailyplans'),
        ),

        # Add a nullable access field, convert user_id to access_ids, then
        # set the column as non-null and finally delete the old user column
        migrations.AddField(
            model_name='teammember',
            name='access',
            field=models.ForeignKey(to='company.Access', null=True, related_name='assignments')
        ),
        migrations.RunSQL(
            "update mehr_handwerk.project_teammember tbl set access_id = ca.id from company_access ca where ca.user_id=tbl.user_id and ca.company_id='mehr_handwerk'"
        ),
        migrations.AlterField(
            model_name='teammember',
            name='access',
            field=models.ForeignKey(related_name='assignments', to='company.Access'),
        ),
        migrations.RemoveField(
            model_name='teammember',
            name='user',
        ),
    ]
