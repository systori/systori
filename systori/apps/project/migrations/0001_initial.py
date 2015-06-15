# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounting', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyPlan',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('day', models.DateField(verbose_name='Day', default=datetime.date.today)),
                ('notes', models.TextField(blank=True)),
                ('equipment', models.ManyToManyField(to='equipment.Equipment', related_name='dailyplans')),
            ],
            options={
                'ordering': ['-day'],
            },
        ),
        migrations.CreateModel(
            name='JobSite',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(verbose_name='Site Name', max_length=512)),
                ('address', models.CharField(verbose_name='Address', max_length=512)),
                ('city', models.CharField(verbose_name='City', max_length=512)),
                ('postal_code', models.CharField(verbose_name='Postal Code', max_length=512)),
                ('country', models.CharField(verbose_name='Country', default='Deutschland', max_length=512)),
                ('latitude', models.FloatField(verbose_name='Latitude', blank=True, null=True)),
                ('longitude', models.FloatField(verbose_name='Longitude', blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(verbose_name='Project Name', max_length=512)),
                ('description', models.TextField(verbose_name='Project Description', blank=True, null=True)),
                ('is_template', models.BooleanField(default=False)),
                ('job_zfill', models.PositiveSmallIntegerField(verbose_name='Job Code Zero Fill', default=1)),
                ('taskgroup_zfill', models.PositiveSmallIntegerField(verbose_name='Task Group Code Zero Fill', default=1)),
                ('task_zfill', models.PositiveSmallIntegerField(verbose_name='Task Code Zero Fill', default=1)),
                ('job_offset', models.PositiveSmallIntegerField(verbose_name='Job Offset', default=0)),
                ('phase', django_fsm.FSMField(choices=[('prospective', 'Prospective'), ('tendering', 'Tendering'), ('planning', 'Planning'), ('executing', 'Executing'), ('settlement', 'Settlement'), ('warranty', 'Warranty'), ('finished', 'Finished')], default='prospective', max_length=50)),
                ('state', django_fsm.FSMField(choices=[('active', 'Active'), ('paused', 'Paused'), ('disputed', 'Disputed'), ('stopped', 'Stopped')], default='active', max_length=50)),
                ('account', models.OneToOneField(to='accounting.Account', related_name='project', null=True)),
            ],
            options={
                'verbose_name_plural': 'Projects',
                'ordering': ['name'],
                'verbose_name': 'Project',
            },
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('is_foreman', models.BooleanField(default=False)),
                ('dailyplan', models.ForeignKey(to='project.DailyPlan', related_name='workers')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='assignments')),
            ],
            options={
                'ordering': ['-is_foreman', 'user__first_name'],
            },
        ),
        migrations.AddField(
            model_name='jobsite',
            name='project',
            field=models.ForeignKey(to='project.Project', related_name='jobsites'),
        ),
        migrations.AddField(
            model_name='dailyplan',
            name='jobsite',
            field=models.ForeignKey(to='project.JobSite', related_name='dailyplans'),
        ),
    ]
