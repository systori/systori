# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import datetime
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0002_dailyplan_tasks'),
        ('accounting', '0004_auto_20160318_2315'),
        ('document', '0003_adjustment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('json', jsonfield.fields.JSONField(default={})),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('document_date', models.DateField(verbose_name='Date', blank=True, default=datetime.date.today)),
                ('notes', models.TextField(blank=True, verbose_name='Notes', null=True)),
                ('letterhead', models.ForeignKey(to='document.Letterhead', related_name='payment_documents')),
                ('project', models.ForeignKey(to='project.Project', related_name='payments')),
                ('transaction', models.OneToOneField(related_name='payment', on_delete=django.db.models.deletion.SET_NULL, to='accounting.Transaction', null=True)),
            ],
            options={
                'verbose_name': 'Payment',
                'verbose_name_plural': 'Payments',
                'ordering': ['id'],
            },
        ),
    ]
