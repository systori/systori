# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import datetime
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0007_auto_20160122_0717'),
        ('project', '0005_remove_project_account'),
        ('document', '0007_auto_20151226_0247'),
    ]

    operations = [
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('json', jsonfield.fields.JSONField(default={})),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('document_date', models.DateField(verbose_name='Date', default=datetime.date.today, blank=True)),
                ('notes', models.TextField(verbose_name='Notes', blank=True, null=True)),
                ('letterhead', models.ForeignKey(to='document.Letterhead', related_name='refund_documents')),
                ('project', models.ForeignKey(to='project.Project', related_name='refunds')),
                ('transaction', models.OneToOneField(null=True, to='accounting.Transaction', on_delete=django.db.models.deletion.SET_NULL, related_name='refund')),
            ],
            options={
                'verbose_name': 'Refund',
                'verbose_name_plural': 'Refunds',
                'ordering': ['id'],
            },
        ),
    ]
