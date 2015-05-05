# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import boardinghouse.base
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Access',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_enabled', models.BooleanField(default=True)),
                ('is_employee', models.BooleanField(default=True)),
                ('is_accountant', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('schema', models.CharField(help_text='The internal name of the schema.<br>May only contain lowercase letters, digits and underscores. Must start with a letter.<br>May not be changed after creation.', validators=[django.core.validators.RegexValidator(message='May only contain lowercase letters, digits and underscores. Must start with a letter.', regex='^[a-z][a-z0-9_]*$')], serialize=False, primary_key=True, unique=True, max_length=36)),
                ('name', models.CharField(help_text='The display name of the schema.', unique=True, max_length=128)),
                ('is_active', models.BooleanField(help_text='Use this instead of deleting schemata.', default=True)),
                ('users', models.ManyToManyField(blank=True, related_name='companies', through='company.Access', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(boardinghouse.base.SharedSchemaMixin, models.Model),
        ),
        migrations.AddField(
            model_name='access',
            name='company',
            field=models.ForeignKey(related_name='users_access', to='company.Company'),
        ),
        migrations.AddField(
            model_name='access',
            name='user',
            field=models.ForeignKey(related_name='companies_access', to=settings.AUTH_USER_MODEL),
        ),
    ]
