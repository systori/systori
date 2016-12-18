# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Access',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('is_owner', models.BooleanField(default=False, verbose_name='Owner', help_text='Owner has full and unlimited Access to Systori.')),
                ('is_staff', models.BooleanField(default=False, verbose_name='staff status', help_text='Designates whether the user can log into this admin site.')),
                ('is_foreman', models.BooleanField(default=False, verbose_name='Foreman', help_text='Foremen can manage laborers.')),
                ('is_laborer', models.BooleanField(default=True, verbose_name='Laborer', help_text='Laborer has limited access to the system.')),
                ('is_accountant', models.BooleanField(default=False, verbose_name='accountant')),
                ('is_active', models.BooleanField(default=True, verbose_name='active', help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts. This will remove user from any present and future daily plans.')),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('schema', models.CharField(primary_key=True, max_length=36, serialize=False, help_text='The internal name of the schema.<br>May only contain lowercase letters, digits and underscores. Must start with a letter.<br>May not be changed after creation.', unique=True, validators=[django.core.validators.RegexValidator(message='May only contain lowercase letters, digits and underscores. Must start with a letter.', regex='^[a-z][a-z0-9_]*$')])),
                ('name', models.CharField(unique=True, max_length=128, help_text='The display name of the schema.')),
                ('is_active', models.BooleanField(default=True, help_text='Use this instead of deleting schemata.')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
