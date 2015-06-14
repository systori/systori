# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0001_initial'),
        ('project', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyplan',
            name='tasks',
            field=models.ManyToManyField(to='task.Task', related_name='dailyplans'),
        ),
        migrations.AddField(
            model_name='dailyplan',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='project.TeamMember', related_name='dailyplans'),
        ),
    ]
