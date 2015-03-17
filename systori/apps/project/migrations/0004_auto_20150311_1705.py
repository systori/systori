# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


def move_address_to_job_site(apps, schema):
    Project = apps.get_model('project', 'Project')
    JobSite = apps.get_model('project', 'JobSite')
    for project in Project.objects.filter(is_template=False).all():
        js = JobSite()

        js.project = project
        js.name = ""

        js.address = project.address
        js.city = project.city
        js.postal_code = project.postal_code
        js.country = project.country

        js.latitude = project.latitude
        js.longitude = project.longitude

        js.save()

class Migration(migrations.Migration):

    dependencies = [
        ('task', '0003_auto_20150211_1721'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project', '0003_auto_20150218_0540'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyPlan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('day', models.DateField(default=datetime.date.today, verbose_name='Day')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobSite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='Site Name', max_length=512)),
                ('address', models.CharField(verbose_name='Address', max_length=512)),
                ('city', models.CharField(verbose_name='City', max_length=512)),
                ('postal_code', models.CharField(verbose_name='Postal Code', max_length=512)),
                ('country', models.CharField(default='Deutschland', verbose_name='Country', max_length=512)),
                ('latitude', models.FloatField(blank=True, verbose_name='Latitude', null=True)),
                ('longitude', models.FloatField(blank=True, verbose_name='Longitude', null=True)),
                ('project', models.ForeignKey(related_name='sites', to='project.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('is_foreman', models.BooleanField(default=False)),
                ('member', models.ForeignKey(related_name='teams', to=settings.AUTH_USER_MODEL)),
                ('plan', models.ForeignKey(related_name='members', to='project.DailyPlan')),
            ],
            options={
                'ordering': ['is_foreman', 'member__first_name'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='dailyplan',
            name='site',
            field=models.ForeignKey(related_name='daily_plans', to='project.JobSite'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dailyplan',
            name='tasks',
            field=models.ManyToManyField(to='task.Task', related_name='daily_plans'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dailyplan',
            name='team',
            field=models.ManyToManyField(through='project.TeamMember', to=settings.AUTH_USER_MODEL, related_name='daily_plans'),
            preserve_default=True,
        ),
        migrations.RunPython(move_address_to_job_site),
        migrations.RemoveField(
            model_name='project',
            name='address',
        ),
        migrations.RemoveField(
            model_name='project',
            name='city',
        ),
        migrations.RemoveField(
            model_name='project',
            name='country',
        ),
        migrations.RemoveField(
            model_name='project',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='project',
            name='longitude',
        ),
        migrations.RemoveField(
            model_name='project',
            name='postal_code',
        ),
    ]
