# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ubrblik.apps.document.models
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0001_initial'),
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('notes', models.TextField(null=True, blank=True, verbose_name='Notes')),
                ('amount', models.DecimalField(verbose_name='Amount', max_digits=12, decimal_places=2)),
                ('header', models.TextField(verbose_name='Header')),
                ('footer', models.TextField(verbose_name='Footer')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('email_pdf', models.FileField(upload_to=ubrblik.apps.document.models.generate_file_path)),
                ('email_latex', models.FileField(upload_to=ubrblik.apps.document.models.generate_file_path)),
                ('print_pdf', models.FileField(upload_to=ubrblik.apps.document.models.generate_file_path)),
                ('print_latex', models.FileField(upload_to=ubrblik.apps.document.models.generate_file_path)),
                ('json', models.FileField(upload_to=ubrblik.apps.document.models.generate_file_path)),
                ('status', django_fsm.FSMField(default='new', choices=[('new', 'New'), ('sent', 'Sent'), ('paid', 'Paid'), ('disputed', 'Disputed')], max_length=50)),
                ('jobs', models.ManyToManyField(related_name='invoices', to='task.Job')),
                ('project', models.ForeignKey(related_name='invoices', to='project.Project')),
            ],
            options={
                'verbose_name_plural': 'Invoices',
                'ordering': ['id'],
                'verbose_name': 'Invoice',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('notes', models.TextField(null=True, blank=True, verbose_name='Notes')),
                ('amount', models.DecimalField(verbose_name='Amount', max_digits=12, decimal_places=2)),
                ('header', models.TextField(verbose_name='Header')),
                ('footer', models.TextField(verbose_name='Footer')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('email_pdf', models.FileField(upload_to=ubrblik.apps.document.models.generate_file_path)),
                ('email_latex', models.FileField(upload_to=ubrblik.apps.document.models.generate_file_path)),
                ('print_pdf', models.FileField(upload_to=ubrblik.apps.document.models.generate_file_path)),
                ('print_latex', models.FileField(upload_to=ubrblik.apps.document.models.generate_file_path)),
                ('json', models.FileField(upload_to=ubrblik.apps.document.models.generate_file_path)),
                ('status', django_fsm.FSMField(default='new', choices=[('new', 'New'), ('sent', 'Sent'), ('approved', 'Approved'), ('declined', 'Declined')], max_length=50)),
                ('jobs', models.ManyToManyField(related_name='proposals', verbose_name='Jobs', to='task.Job')),
                ('project', models.ForeignKey(related_name='proposals', to='project.Project')),
            ],
            options={
                'verbose_name_plural': 'Proposals',
                'ordering': ['id'],
                'verbose_name': 'Proposal',
            },
            bases=(models.Model,),
        ),
    ]
