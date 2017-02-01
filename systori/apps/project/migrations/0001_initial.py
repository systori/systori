# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0001_initial'),
        ('equipment', '0001_initial'),
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyPlan',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('day', models.DateField(default=datetime.date.today, verbose_name='Day')),
                ('notes', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['-day'],
            },
        ),
        migrations.CreateModel(
            name='JobSite',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=512, verbose_name='Site Name')),
                ('address', models.CharField(max_length=512, verbose_name='Address')),
                ('city', models.CharField(max_length=512, verbose_name='City')),
                ('postal_code', models.CharField(max_length=512, verbose_name='Postal Code')),
                ('country', models.CharField(max_length=512, default='Deutschland', verbose_name='Country')),
                ('latitude', models.FloatField(null=True, verbose_name='Latitude', blank=True)),
                ('longitude', models.FloatField(null=True, verbose_name='Longitude', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=512, verbose_name='Project Name')),
                ('description', models.TextField(null=True, verbose_name='Project Description', blank=True)),
                ('is_template', models.BooleanField(default=False)),
                ('job_zfill', models.PositiveSmallIntegerField(default=1, verbose_name='Job Code Zero Fill')),
                ('taskgroup_zfill', models.PositiveSmallIntegerField(default=1, verbose_name='Task Group Code Zero Fill')),
                ('task_zfill', models.PositiveSmallIntegerField(default=1, verbose_name='Task Code Zero Fill')),
                ('phase', django_fsm.FSMField(max_length=50, default='prospective', choices=[('prospective', 'Prospective'), ('tendering', 'Tendering'), ('planning', 'Planning'), ('executing', 'Executing'), ('settlement', 'Settlement'), ('warranty', 'Warranty'), ('finished', 'Finished')])),
                ('state', django_fsm.FSMField(max_length=50, default='active', choices=[('active', 'Active'), ('paused', 'Paused'), ('disputed', 'Disputed'), ('stopped', 'Stopped')])),
                ('account', models.OneToOneField(to='accounting.Account', related_name='project', null=True, on_delete=models.SET_NULL)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Project',
                'verbose_name_plural': 'Projects',
            },
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('is_foreman', models.BooleanField(default=False)),
                ('access', models.ForeignKey(to='company.Access', related_name='assignments', on_delete=models.CASCADE)),
                ('dailyplan', models.ForeignKey(to='project.DailyPlan', related_name='workers', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['-is_foreman', 'access__user__first_name'],
            },
        ),
        migrations.AddField(
            model_name='jobsite',
            name='project',
            field=models.ForeignKey(to='project.Project', related_name='jobsites', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='dailyplan',
            name='accesses',
            field=models.ManyToManyField(through='project.TeamMember', to='company.Access', related_name='dailyplans'),
        ),
        migrations.AddField(
            model_name='dailyplan',
            name='equipment',
            field=models.ManyToManyField(to='equipment.Equipment', related_name='dailyplans'),
        ),
        migrations.AddField(
            model_name='dailyplan',
            name='jobsite',
            field=models.ForeignKey(to='project.JobSite', related_name='dailyplans', on_delete=models.CASCADE),
        ),
    ]
