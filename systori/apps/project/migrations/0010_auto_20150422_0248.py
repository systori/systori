# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_fsm


def update_project_phase(apps, schema):
    Project = apps.get_model('project', 'Project')
    Job = apps.get_model('task', 'Job')
    Proposal = apps.get_model('document', 'Proposal')
    for project in Project.objects.filter(is_template=False).all():
        if Job.objects.filter(project_id=project.id, status='started').exists():
            print('executing')
            project.phase = 'executing'
            project.save()
        elif Proposal.objects.filter(project_id=project.id, status='approved').exists():
            print('planning')
            project.phase = 'planning'
            project.save()
        elif Proposal.objects.filter(project_id=project.id).exists():
            print('tendering')
            project.phase = 'tendering'
            project.save()

class Migration(migrations.Migration):

    dependencies = [
        ('project', '0009_project_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='phase',
            field=django_fsm.FSMField(default='prospective', max_length=50, choices=[('prospective', 'Prospective'), ('tendering', 'Tendering'), ('planning', 'Planning'), ('executing', 'Executing'), ('settlement', 'Settlement'), ('warranty', 'Warranty'), ('finished', 'Finished')]),
        ),
        migrations.AddField(
            model_name='project',
            name='state',
            field=django_fsm.FSMField(default='active', max_length=50, choices=[('active', 'Active'), ('paused', 'Paused'), ('canceled', 'Canceled'), ('disputed', 'Disputed'), ('stopped', 'Stopped')]),
        ),
        migrations.RunPython(update_project_phase)
    ]
