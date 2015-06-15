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
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('business', models.CharField(verbose_name='Business', blank=True, max_length=512)),
                ('salutation', models.CharField(verbose_name='Salutation', blank=True, max_length=512)),
                ('first_name', models.CharField(verbose_name='First Name', max_length=512)),
                ('last_name', models.CharField(verbose_name='Last Name', max_length=512)),
                ('phone', models.CharField(verbose_name='Phone', max_length=512)),
                ('email', models.EmailField(verbose_name='Email', blank=True, max_length=254)),
                ('website', models.URLField(verbose_name='Website', blank=True)),
                ('address', models.CharField(verbose_name='Address', max_length=512)),
                ('postal_code', models.CharField(verbose_name='Postal Code', max_length=512)),
                ('city', models.CharField(verbose_name='City', max_length=512)),
                ('country', models.CharField(verbose_name='Country', default='Deutschland', max_length=512)),
                ('notes', models.TextField(verbose_name='Notes', blank=True)),
            ],
            options={
                'verbose_name_plural': 'Contacts',
                'ordering': ['business', 'last_name'],
                'verbose_name': 'Contact',
            },
        ),
        migrations.CreateModel(
            name='ProjectContact',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('association', models.CharField(verbose_name='Association', choices=[('customer', 'Customer'), ('contractor', 'Contractor'), ('supplier', 'Supplier'), ('architect', 'Architect'), ('other', 'Other')], default='customer', max_length=128)),
                ('is_billable', models.BooleanField(verbose_name='Is Billable?', default=False)),
                ('notes', models.TextField(verbose_name='Notes', blank=True)),
                ('contact', models.ForeignKey(to='directory.Contact', related_name='project_contacts')),
            ],
            options={
                'verbose_name_plural': 'Project Contacts',
                'ordering': ['association', 'id'],
                'verbose_name': 'Project Contact',
            },
        ),
    ]
