# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0001_initial'),
        ('company', '0001_initial'),
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=512, verbose_name='Job Name')),
                ('job_code', models.PositiveSmallIntegerField(default=0, verbose_name='Code')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('taskgroup_offset', models.PositiveSmallIntegerField(default=0, verbose_name='Task Group Offset')),
                ('billing_method', models.CharField(max_length=128, default='fixed_price', choices=[('fixed_price', 'Fixed Price'), ('time_and_materials', 'Time and Materials')], verbose_name='Billing Method')),
                ('is_revenue_recognized', models.BooleanField(default=False)),
                ('status', django_fsm.FSMField(max_length=50, default='draft', choices=[('draft', 'Draft'), ('proposed', 'Proposed'), ('approved', 'Approved'), ('started', 'Started'), ('completed', 'Completed')])),
                ('account', models.OneToOneField(to='accounting.Account', on_delete=django.db.models.deletion.SET_NULL, related_name='job', null=True)),
                ('project', models.ForeignKey(to='project.Project', related_name='jobs', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['job_code'],
                'verbose_name': 'Job',
                'verbose_name_plural': 'Job',
            },
        ),
        migrations.CreateModel(
            name='LineItem',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=512, verbose_name='Name')),
                ('unit_qty', models.DecimalField(max_digits=14, default=0.0, verbose_name='Quantity', decimal_places=4)),
                ('task_qty', models.DecimalField(max_digits=14, default=0.0, verbose_name='Quantity', decimal_places=4)),
                ('billable', models.DecimalField(max_digits=14, default=0.0, verbose_name='Billable', decimal_places=4)),
                ('unit', models.CharField(max_length=64, verbose_name='Unit')),
                ('price', models.DecimalField(max_digits=14, default=0.0, verbose_name='Price', decimal_places=4)),
                ('is_labor', models.BooleanField(default=False)),
                ('is_material', models.BooleanField(default=False)),
                ('is_flagged', models.BooleanField(default=False)),
                ('is_correction', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['id'],
                'verbose_name': 'Line Item',
                'verbose_name_plural': 'Line Items',
            },
        ),
        migrations.CreateModel(
            name='ProgressAttachment',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('attachment', models.FileField(upload_to='')),
            ],
            options={
                'ordering': ('id',),
                'verbose_name': 'Attachment',
                'verbose_name_plural': 'Attachments',
            },
        ),
        migrations.CreateModel(
            name='ProgressReport',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('comment', models.TextField()),
                ('complete', models.DecimalField(max_digits=14, default=0.0, verbose_name='Complete', decimal_places=4)),
                ('access', models.ForeignKey(to='company.Access', related_name='filedreports', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('-timestamp',),
                'verbose_name': 'Progress Report',
                'verbose_name_plural': 'Progress Reports',
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('order', models.PositiveIntegerField(db_index=True, editable=False)),
                ('name', models.CharField(max_length=512, verbose_name='Name')),
                ('description', models.TextField()),
                ('qty', models.DecimalField(max_digits=14, default=0.0, verbose_name='Quantity', decimal_places=4)),
                ('unit', models.CharField(max_length=64, verbose_name='Unit')),
                ('complete', models.DecimalField(max_digits=14, default=0.0, verbose_name='Complete', decimal_places=4)),
                ('is_optional', models.BooleanField(default=False)),
                ('started_on', models.DateField(null=True, blank=True)),
                ('completed_on', models.DateField(null=True, blank=True)),
                ('status', django_fsm.FSMField(max_length=50, choices=[('approved', 'Approved'), ('ready', 'Ready'), ('running', 'Running'), ('done', 'Done')], blank=True)),
            ],
            options={
                'ordering': ('order',),
                'verbose_name': 'Task',
                'verbose_name_plural': 'Task',
            },
        ),
        migrations.CreateModel(
            name='TaskGroup',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('order', models.PositiveIntegerField(db_index=True, editable=False)),
                ('name', models.CharField(max_length=512, verbose_name='Name')),
                ('description', models.TextField(blank=True)),
                ('job', models.ForeignKey(to='task.Job', related_name='taskgroups', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['order'],
                'verbose_name': 'Task Group',
                'verbose_name_plural': 'Task Groups',
            },
        ),
        migrations.CreateModel(
            name='TaskInstance',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('order', models.PositiveIntegerField(db_index=True, editable=False)),
                ('name', models.CharField(max_length=512, verbose_name='Name')),
                ('description', models.TextField()),
                ('selected', models.BooleanField(default=False)),
                ('task', models.ForeignKey(to='task.Task', related_name='taskinstances', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['order'],
                'verbose_name': 'Task Instance',
                'verbose_name_plural': 'Task Instances',
            },
        ),
        migrations.AddField(
            model_name='task',
            name='taskgroup',
            field=models.ForeignKey(to='task.TaskGroup', related_name='tasks', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='progressreport',
            name='task',
            field=models.ForeignKey(to='task.Task', related_name='progressreports', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='progressattachment',
            name='report',
            field=models.ForeignKey(to='task.ProgressReport', related_name='attachments', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='lineitem',
            name='taskinstance',
            field=models.ForeignKey(to='task.TaskInstance', related_name='lineitems', on_delete=models.CASCADE),
        ),
    ]
