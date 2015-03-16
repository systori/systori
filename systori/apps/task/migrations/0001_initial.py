# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('project', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('order', models.PositiveIntegerField(editable=False, db_index=True)),
                ('name', models.CharField(verbose_name='Job Name', max_length=512)),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('billing_method', models.CharField(verbose_name='Billing Method', max_length=128, choices=[('fixed_price', 'Fixed Price'), ('time_and_materials', 'Time and Materials')], default='fixed_price')),
                ('status', django_fsm.FSMField(max_length=50, choices=[('draft', 'Draft'), ('proposed', 'Proposed'), ('approved', 'Approved'), ('started', 'Started'), ('completed', 'Completed')], default='draft')),
                ('project', models.ForeignKey(to='project.Project', related_name='jobs')),
            ],
            options={
                'verbose_name_plural': 'Job',
                'verbose_name': 'Job',
                'ordering': ['order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LineItem',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='Name', max_length=512)),
                ('unit_qty', models.DecimalField(verbose_name='Quantity', default=0.0, decimal_places=4, max_digits=14)),
                ('task_qty', models.DecimalField(verbose_name='Quantity', default=0.0, decimal_places=4, max_digits=14)),
                ('billable', models.DecimalField(verbose_name='Billable', default=0.0, decimal_places=4, max_digits=14)),
                ('unit', models.CharField(verbose_name='Unit', max_length=64)),
                ('price', models.DecimalField(verbose_name='Price', default=0.0, decimal_places=4, max_digits=14)),
                ('is_labor', models.BooleanField(default=False)),
                ('is_material', models.BooleanField(default=False)),
                ('is_flagged', models.BooleanField(default=False)),
                ('is_correction', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Line Items',
                'verbose_name': 'Line Item',
                'ordering': ['id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProgressAttachment',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('attachment', models.FileField(upload_to='')),
            ],
            options={
                'verbose_name_plural': 'Attachments',
                'verbose_name': 'Attachment',
                'ordering': ['id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProgressReport',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('comment', models.TextField()),
                ('complete', models.DecimalField(verbose_name='Complete', default=0.0, decimal_places=4, max_digits=14)),
            ],
            options={
                'verbose_name_plural': 'Progress Reports',
                'verbose_name': 'Progress Report',
                'ordering': ['date'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('order', models.PositiveIntegerField(editable=False, db_index=True)),
                ('name', models.CharField(verbose_name='Name', max_length=512)),
                ('description', models.TextField()),
                ('qty', models.DecimalField(verbose_name='Quantity', default=0.0, decimal_places=4, max_digits=14)),
                ('unit', models.CharField(verbose_name='Unit', max_length=64)),
                ('complete', models.DecimalField(verbose_name='Complete', default=0.0, decimal_places=4, max_digits=14)),
                ('is_optional', models.BooleanField(default=False)),
                ('started_on', models.DateField(null=True, blank=True)),
                ('completed_on', models.DateField(null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'Task',
                'verbose_name': 'Task',
                'ordering': ['id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaskGroup',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('order', models.PositiveIntegerField(editable=False, db_index=True)),
                ('name', models.CharField(verbose_name='Name', max_length=512)),
                ('description', models.TextField(blank=True)),
                ('job', models.ForeignKey(to='task.Job', related_name='taskgroups')),
            ],
            options={
                'verbose_name_plural': 'Task Groups',
                'verbose_name': 'Task Group',
                'ordering': ['id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaskInstance',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('order', models.PositiveIntegerField(editable=False, db_index=True)),
                ('name', models.CharField(verbose_name='Name', max_length=512)),
                ('description', models.TextField()),
                ('selected', models.BooleanField(default=False)),
                ('task', models.ForeignKey(to='task.Task', related_name='taskinstances')),
            ],
            options={
                'verbose_name_plural': 'Task Instances',
                'verbose_name': 'Task Instance',
                'ordering': ['id'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='task',
            name='taskgroup',
            field=models.ForeignKey(to='task.TaskGroup', related_name='tasks'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='progressreport',
            name='task',
            field=models.ForeignKey(to='task.Task', related_name='reports'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='progressattachment',
            name='report',
            field=models.ForeignKey(to='task.ProgressReport', related_name='attachments'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='lineitem',
            name='taskinstance',
            field=models.ForeignKey(to='task.TaskInstance', related_name='lineitems'),
            preserve_default=True,
        ),
    ]
