# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('business', models.CharField(max_length=512, verbose_name='Business', blank=True)),
                ('salutation', models.CharField(max_length=512, verbose_name='Salutation', blank=True)),
                ('first_name', models.CharField(verbose_name='First Name', max_length=512)),
                ('last_name', models.CharField(verbose_name='Last Name', max_length=512)),
                ('phone', models.CharField(verbose_name='Phone', max_length=512)),
                ('email', models.EmailField(max_length=75, verbose_name='Email', blank=True)),
                ('website', models.URLField(verbose_name='Website', blank=True)),
                ('address', models.CharField(verbose_name='Address', max_length=512)),
                ('postal_code', models.CharField(verbose_name='Postal Code', max_length=512)),
                ('city', models.CharField(verbose_name='City', max_length=512)),
                ('country', models.CharField(max_length=512, verbose_name='Country', blank=True)),
                ('notes', models.TextField(verbose_name='Notes', blank=True)),
            ],
            options={
                'verbose_name_plural': 'Contacts',
                'ordering': ['business', 'last_name'],
                'verbose_name': 'Contact',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('association', models.CharField(default='customer', choices=[('customer', 'Customer'), ('contractor', 'Contractor'), ('supplier', 'Supplier'), ('architect', 'Architect'), ('other', 'Other')], verbose_name='Association', max_length=128)),
                ('is_billable', models.BooleanField(default=False, verbose_name='Is Billable?')),
                ('notes', models.TextField(verbose_name='Notes', blank=True)),
                ('contact', models.ForeignKey(related_name='project_contacts', to='directory.Contact')),
                ('project', models.ForeignKey(related_name='project_contacts', to='project.Project')),
            ],
            options={
                'verbose_name_plural': 'Project Contacts',
                'ordering': ['association', 'id'],
                'verbose_name': 'Project Contact',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='contact',
            name='projects',
            field=models.ManyToManyField(related_name='contacts', through='directory.ProjectContact', to='project.Project'),
            preserve_default=True,
        ),
    ]
