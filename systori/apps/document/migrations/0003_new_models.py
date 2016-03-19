# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import jsonfield.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0003_added_value_fields'),
        ('project', '0002_dailyplan_tasks'),
        ('document', '0002_auto_20160221_0254'),
    ]

    operations = [
        migrations.CreateModel(
            name='Adjustment',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('json', jsonfield.fields.JSONField(default={})),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('document_date', models.DateField(blank=True, default=datetime.date.today, verbose_name='Date')),
                ('notes', models.TextField(null=True, verbose_name='Notes', blank=True)),
                ('invoice', models.OneToOneField(null=True, to='document.Invoice', on_delete=django.db.models.deletion.SET_NULL, related_name='adjustment')),
                ('letterhead', models.ForeignKey(to='document.Letterhead', related_name='adjustment_documents')),
                ('project', models.ForeignKey(to='project.Project', related_name='adjustments')),
                ('transaction', models.OneToOneField(null=True, to='accounting.Transaction', on_delete=django.db.models.deletion.SET_NULL, related_name='adjustment')),
            ],
            options={
                'ordering': ['id'],
                'verbose_name': 'Adjustment',
                'verbose_name_plural': 'Adjustment',
            },
        ),
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
