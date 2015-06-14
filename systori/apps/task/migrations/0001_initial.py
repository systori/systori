# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('order', models.PositiveIntegerField(editable=False, db_index=True)),
                ('name', models.CharField(verbose_name='Job Name', max_length=512)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('taskgroup_offset', models.PositiveSmallIntegerField(verbose_name='Task Group Offset', default=0)),
                ('billing_method', models.CharField(verbose_name='Billing Method', choices=[('fixed_price', 'Fixed Price'), ('time_and_materials', 'Time and Materials')], default='fixed_price', max_length=128)),
                ('status', django_fsm.FSMField(choices=[('draft', 'Draft'), ('proposed', 'Proposed'), ('approved', 'Approved'), ('started', 'Started'), ('completed', 'Completed')], default='draft', max_length=50)),
                ('project', models.ForeignKey(to='project.Project', related_name='jobs')),
            ],
            options={
                'verbose_name_plural': 'Job',
                'ordering': ['order'],
                'verbose_name': 'Job',
            },
        ),
        migrations.CreateModel(
            name='LineItem',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(verbose_name='Name', max_length=512)),
                ('unit_qty', models.DecimalField(max_digits=14, verbose_name='Quantity', default=0.0, decimal_places=4)),
                ('task_qty', models.DecimalField(max_digits=14, verbose_name='Quantity', default=0.0, decimal_places=4)),
                ('billable', models.DecimalField(max_digits=14, verbose_name='Billable', default=0.0, decimal_places=4)),
                ('unit', models.CharField(verbose_name='Unit', max_length=64)),
                ('price', models.DecimalField(max_digits=14, verbose_name='Price', default=0.0, decimal_places=4)),
                ('is_labor', models.BooleanField(default=False)),
                ('is_material', models.BooleanField(default=False)),
                ('is_flagged', models.BooleanField(default=False)),
                ('is_correction', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Line Items',
                'ordering': ['id'],
                'verbose_name': 'Line Item',
            },
        ),
        migrations.CreateModel(
            name='ProgressAttachment',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('attachment', models.FileField(upload_to='')),
            ],
            options={
                'verbose_name_plural': 'Attachments',
                'ordering': ['id'],
                'verbose_name': 'Attachment',
            },
        ),
        migrations.CreateModel(
            name='ProgressReport',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('comment', models.TextField()),
                ('complete', models.DecimalField(max_digits=14, verbose_name='Complete', default=0.0, decimal_places=4)),
            ],
            options={
                'verbose_name_plural': 'Progress Reports',
                'ordering': ['-timestamp'],
                'verbose_name': 'Progress Report',
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('order', models.PositiveIntegerField(editable=False, db_index=True)),
                ('name', models.CharField(verbose_name='Name', max_length=512)),
                ('description', models.TextField()),
                ('qty', models.DecimalField(max_digits=14, verbose_name='Quantity', default=0.0, decimal_places=4)),
                ('unit', models.CharField(verbose_name='Unit', max_length=64)),
                ('complete', models.DecimalField(max_digits=14, verbose_name='Complete', default=0.0, decimal_places=4)),
                ('is_optional', models.BooleanField(default=False)),
                ('started_on', models.DateField(blank=True, null=True)),
                ('completed_on', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Task',
                'ordering': ['order'],
                'verbose_name': 'Task',
            },
        ),
        migrations.CreateModel(
            name='TaskGroup',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('order', models.PositiveIntegerField(editable=False, db_index=True)),
                ('name', models.CharField(verbose_name='Name', max_length=512)),
                ('description', models.TextField(blank=True)),
                ('job', models.ForeignKey(to='task.Job', related_name='taskgroups')),
            ],
            options={
                'verbose_name_plural': 'Task Groups',
                'ordering': ['order'],
                'verbose_name': 'Task Group',
            },
        ),
        migrations.CreateModel(
            name='TaskInstance',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('order', models.PositiveIntegerField(editable=False, db_index=True)),
                ('name', models.CharField(verbose_name='Name', max_length=512)),
                ('description', models.TextField()),
                ('selected', models.BooleanField(default=False)),
                ('task', models.ForeignKey(to='task.Task', related_name='taskinstances')),
            ],
            options={
                'verbose_name_plural': 'Task Instances',
                'ordering': ['order'],
                'verbose_name': 'Task Instance',
            },
        ),
        migrations.AddField(
            model_name='task',
            name='taskgroup',
            field=models.ForeignKey(to='task.TaskGroup', related_name='tasks'),
        ),
        migrations.AddField(
            model_name='progressreport',
            name='task',
            field=models.ForeignKey(to='task.Task', related_name='progressreports'),
        ),
        migrations.AddField(
            model_name='progressreport',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='filedreports'),
        ),
        migrations.AddField(
            model_name='progressattachment',
            name='report',
            field=models.ForeignKey(to='task.ProgressReport', related_name='attachments'),
        ),
        migrations.AddField(
            model_name='lineitem',
            name='taskinstance',
            field=models.ForeignKey(to='task.TaskInstance', related_name='lineitems'),
        ),
    ]
