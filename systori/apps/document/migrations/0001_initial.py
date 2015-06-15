# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django_fsm
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentTemplate',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(verbose_name='Name', max_length=512)),
                ('header', models.TextField(verbose_name='Header')),
                ('footer', models.TextField(verbose_name='Footer')),
                ('document_type', models.CharField(verbose_name='Document Type', choices=[('proposal', 'Proposal'), ('invoice', 'Invoice')], default='proposal', max_length=128)),
            ],
            options={
                'verbose_name_plural': 'Document Templates',
                'ordering': ['name'],
                'verbose_name': 'Document Template',
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('json', jsonfield.fields.JSONField(default={})),
                ('json_version', models.CharField(max_length=5)),
                ('amount', models.DecimalField(max_digits=12, verbose_name='Amount', decimal_places=2)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('document_date', models.DateField(verbose_name='Date', blank=True, default=datetime.date.today)),
                ('notes', models.TextField(verbose_name='Notes', blank=True, null=True)),
                ('invoice_no', models.CharField(verbose_name='Invoice No.', max_length=30)),
                ('status', django_fsm.FSMField(choices=[('new', 'New'), ('sent', 'Sent'), ('paid', 'Paid'), ('disputed', 'Disputed')], default='new', max_length=50)),
            ],
            options={
                'verbose_name_plural': 'Invoices',
                'ordering': ['id'],
                'verbose_name': 'Invoice',
            },
        ),
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('json', jsonfield.fields.JSONField(default={})),
                ('json_version', models.CharField(max_length=5)),
                ('amount', models.DecimalField(max_digits=12, verbose_name='Amount', decimal_places=2)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('document_date', models.DateField(verbose_name='Date', blank=True, default=datetime.date.today)),
                ('notes', models.TextField(verbose_name='Notes', blank=True, null=True)),
                ('status', django_fsm.FSMField(choices=[('new', 'New'), ('sent', 'Sent'), ('approved', 'Approved'), ('declined', 'Declined')], default='new', max_length=50)),
            ],
            options={
                'verbose_name_plural': 'Proposals',
                'ordering': ['id'],
                'verbose_name': 'Proposal',
            },
        ),
    ]
