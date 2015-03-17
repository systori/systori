# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import systori.apps.document.models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0003_auto_20150211_1721'),
        ('project', '0007_auto_20150317_2027'),
        ('document', '0005_auto_20150312_1902'),
    ]

    operations = [
        migrations.CreateModel(
            name='Evidence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('notes', models.TextField(verbose_name='Notes', null=True, blank=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('document_date', models.DateField(verbose_name='Date', blank=True, default=datetime.date.today)),
                ('print_pdf', models.FileField(upload_to=systori.apps.document.models.generate_file_path)),
                ('print_latex', models.FileField(upload_to=systori.apps.document.models.generate_file_path)),
                ('json', models.FileField(upload_to=systori.apps.document.models.generate_file_path)),
                ('jobs', models.ManyToManyField(to='task.Job', related_name='evidences')),
                ('project', models.ForeignKey(to='project.Project', related_name='evidences')),
            ],
            options={
                'verbose_name': 'Invoice',
                'ordering': ['id'],
                'verbose_name_plural': 'Invoices',
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='documenttemplate',
            name='document_type',
            field=models.CharField(verbose_name='Document Type', max_length=128, default='proposal', choices=[('proposal', 'Proposal'), ('invoice', 'Invoice'), ('evidence', 'Evidence')]),
            preserve_default=True,
        ),
    ]
