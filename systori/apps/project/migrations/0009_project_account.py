# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def add_accounts(apps, schema):
    Account = apps.get_model('accounting', 'Account')
    Project = apps.get_model('project', 'Project')
    for project in Project.objects.filter(is_template=False).all():
        project.account = Account.objects.create(account_type='asset', code='1{:04}'.format(project.id))
        project.save()

class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0001_initial'),
        ('project', '0008_dailyplan_equipment'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='account',
            field=models.OneToOneField(null=True, related_name='project', to='accounting.Account'),
            preserve_default=True,
        ),
        migrations.RunPython(add_accounts)
    ]
