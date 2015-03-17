# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ubrblik.apps.document.models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0003_auto_20150211_1721'),
        ('project', '0006_auto_20150313_2036'),
        ('document', '0005_auto_20150312_1902'),
    ]

    operations = [
        migrations.CreateModel(
            name='Evidence',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('notes', models.TextField(null=True, verbose_name='Notes', blank=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Amount')),
                ('header', models.TextField(verbose_name='Header')),
                ('footer', models.TextField(verbose_name='Footer')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('document_date', models.DateField(default=datetime.date.today, verbose_name='Date', blank=True)),
                ('email_pdf', models.FileField(upload_to=ubrblik.apps.document.models.generate_file_path)),
                ('email_latex', models.FileField(upload_to=ubrblik.apps.document.models.generate_file_path)),
                ('print_pdf', models.FileField(upload_to=ubrblik.apps.document.models.generate_file_path)),
                ('print_latex', models.FileField(upload_to=ubrblik.apps.document.models.generate_file_path)),
                ('json', models.FileField(upload_to=ubrblik.apps.document.models.generate_file_path)),
                ('jobs', models.ManyToManyField(to='task.Job', related_name='evidences')),
                ('project', models.ForeignKey(to='project.Project', related_name='evidences')),
            ],
            options={
                'ordering': ['id'],
                'verbose_name': 'Invoice',
                'verbose_name_plural': 'Invoices',
            },
            bases=(models.Model,),
        ),
    ]
