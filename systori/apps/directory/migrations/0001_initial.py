# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('business', models.CharField(max_length=512, verbose_name='Business', blank=True)),
                ('salutation', models.CharField(max_length=512, verbose_name='Salutation', blank=True)),
                ('first_name', models.CharField(max_length=512, verbose_name='First Name')),
                ('last_name', models.CharField(max_length=512, verbose_name='Last Name')),
                ('phone', models.CharField(max_length=512, verbose_name='Phone')),
                ('email', models.EmailField(max_length=254, verbose_name='Email', blank=True)),
                ('website', models.URLField(verbose_name='Website', blank=True)),
                ('address', models.CharField(max_length=512, verbose_name='Address')),
                ('postal_code', models.CharField(max_length=512, verbose_name='Postal Code')),
                ('city', models.CharField(max_length=512, verbose_name='City')),
                ('country', models.CharField(max_length=512, default='Deutschland', verbose_name='Country')),
                ('is_address_label_generated', models.BooleanField(default=True, verbose_name='auto-generate address label')),
                ('address_label', models.TextField(verbose_name='Address Label', blank=True)),
                ('notes', models.TextField(verbose_name='Notes', blank=True)),
            ],
            options={
                'ordering': ['first_name', 'last_name'],
                'verbose_name': 'Contact',
                'verbose_name_plural': 'Contacts',
            },
        ),
        migrations.CreateModel(
            name='ProjectContact',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('association', models.CharField(max_length=128, default='customer', choices=[('customer', 'Customer'), ('contractor', 'Contractor'), ('supplier', 'Supplier'), ('architect', 'Architect'), ('other', 'Other')], verbose_name='Association')),
                ('is_billable', models.BooleanField(default=False, verbose_name='Is Billable?')),
                ('notes', models.TextField(verbose_name='Notes', blank=True)),
                ('contact', models.ForeignKey(to='directory.Contact', related_name='project_contacts')),
            ],
            options={
                'ordering': ['association', 'id'],
                'verbose_name': 'Project Contact',
                'verbose_name_plural': 'Project Contacts',
            },
        ),
    ]
