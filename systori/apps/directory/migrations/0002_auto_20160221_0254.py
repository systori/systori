# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
        ('directory', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectcontact',
            name='project',
            field=models.ForeignKey(to='project.Project', related_name='project_contacts', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='contact',
            name='projects',
            field=models.ManyToManyField(through='directory.ProjectContact', to='project.Project', related_name='contacts'),
        ),
    ]
