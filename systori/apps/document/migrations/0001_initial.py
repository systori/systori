# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from decimal import Decimal
import jsonfield.fields
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentSettings',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('language', models.CharField(unique=True, max_length=2, default='de', choices=[('de', 'Deutsch'), ('en', 'English')], verbose_name='language')),
            ],
        ),
        migrations.CreateModel(
            name='DocumentTemplate',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=512, verbose_name='Name')),
                ('header', models.TextField(verbose_name='Header')),
                ('footer', models.TextField(verbose_name='Footer')),
                ('document_type', models.CharField(max_length=128, default='proposal', choices=[('proposal', 'Proposal'), ('invoice', 'Invoice')], verbose_name='Document Type')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Document Template',
                'verbose_name_plural': 'Document Templates',
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('json', jsonfield.fields.JSONField(default={})),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('document_date', models.DateField(default=datetime.date.today, verbose_name='Date', blank=True)),
                ('notes', models.TextField(null=True, verbose_name='Notes', blank=True)),
                ('invoice_no', models.CharField(max_length=30, verbose_name='Invoice No.')),
                ('status', django_fsm.FSMField(max_length=50, default='draft', choices=[('draft', 'Draft'), ('sent', 'Sent'), ('paid', 'Paid')])),
            ],
            options={
                'ordering': ['id'],
                'verbose_name': 'Invoice',
                'verbose_name_plural': 'Invoices',
            },
        ),
        migrations.CreateModel(
            name='Letterhead',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=512, verbose_name='Name')),
                ('letterhead_pdf', models.FileField(upload_to='letterhead', verbose_name='Letterhead PDF')),
                ('document_unit', models.CharField(max_length=5, default='mm', choices=[('mm', 'mm'), ('cm', 'cm'), ('inch', 'inch')], verbose_name='Document Unit')),
                ('top_margin', models.DecimalField(max_digits=4, default=Decimal('25'), verbose_name='Top Margin', decimal_places=2)),
                ('right_margin', models.DecimalField(max_digits=4, default=Decimal('25'), verbose_name='Right Margin', decimal_places=2)),
                ('bottom_margin', models.DecimalField(max_digits=4, default=Decimal('25'), verbose_name='Bottom Margin', decimal_places=2)),
                ('left_margin', models.DecimalField(max_digits=4, default=Decimal('25'), verbose_name='Left Margin', decimal_places=2)),
                ('top_margin_next', models.DecimalField(max_digits=4, default=Decimal('25'), verbose_name='Top Margin Next', decimal_places=2)),
                ('bottom_margin_next', models.DecimalField(max_digits=4, default=Decimal('25'), verbose_name='Bottom Margin Next', decimal_places=2)),
                ('document_format', models.CharField(max_length=30, default='A4', choices=[('A5', 'A5'), ('A4', 'A4'), ('A3', 'A3'), ('LETTER', 'LETTER'), ('LEGAL', 'LEGAL'), ('ELEVENSEVENTEEN', 'ELEVENSEVENTEEN'), ('B5', 'B5'), ('B4', 'B4')], verbose_name='Pagesize')),
                ('orientation', models.CharField(max_length=15, default='portrait', choices=[('portrait', 'Portrait'), ('landscape', 'Landscape')], verbose_name='Orientation')),
                ('debug', models.BooleanField(default=True, verbose_name='Debug Mode')),
            ],
        ),
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('json', jsonfield.fields.JSONField(default={})),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('document_date', models.DateField(default=datetime.date.today, verbose_name='Date', blank=True)),
                ('notes', models.TextField(null=True, verbose_name='Notes', blank=True)),
                ('status', django_fsm.FSMField(max_length=50, default='new', choices=[('new', 'New'), ('sent', 'Sent'), ('approved', 'Approved'), ('declined', 'Declined')])),
            ],
            options={
                'ordering': ['id'],
                'verbose_name': 'Proposal',
                'verbose_name_plural': 'Proposals',
            },
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('json', jsonfield.fields.JSONField(default={})),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('document_date', models.DateField(default=datetime.date.today, verbose_name='Date', blank=True)),
                ('notes', models.TextField(null=True, verbose_name='Notes', blank=True)),
                ('letterhead', models.ForeignKey(to='document.Letterhead', related_name='refund_documents')),
            ],
            options={
                'ordering': ['id'],
                'verbose_name': 'Refund',
                'verbose_name_plural': 'Refunds',
            },
        ),
    ]
