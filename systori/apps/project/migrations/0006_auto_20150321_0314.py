# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project', '0005_auto_20150318_1726'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='teammember',
            options={'ordering': ['-is_foreman', 'user__first_name']},
        ),
        migrations.RemoveField(
            model_name='dailyplan',
            name='team',
        ),
        migrations.RemoveField(
            model_name='teammember',
            name='member',
        ),
        migrations.RemoveField(
            model_name='teammember',
            name='plan',
        ),
        migrations.AddField(
            model_name='dailyplan',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='dailyplans', through='project.TeamMember'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='teammember',
            name='dailyplan',
            field=models.ForeignKey(to='project.DailyPlan', default=None, related_name='workers'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='teammember',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, default=None, related_name='assignments'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='dailyplan',
            name='jobsite',
            field=models.ForeignKey(related_name='dailyplans', to='project.JobSite'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dailyplan',
            name='tasks',
            field=models.ManyToManyField(to='task.Task', related_name='dailyplans'),
            preserve_default=True,
        ),
    ]
