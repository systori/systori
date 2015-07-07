# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import systori.apps.user.models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_auto_20150422_0248'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ('first_name',), 'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', systori.apps.user.models.UserManager()),
            ],
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_foreman',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_laborer',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_staff',
        ),
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
        # Altering email column is a two step process, first we allow NULLs in email,
        # second update all blank emails to be NULL, then finally apply
        # the unique constraint.
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(null=True),
        ),
        migrations.RunSQL(
            "update user_user set email=null where email=''"
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(verbose_name='email address', null=True, blank=True, unique=True, max_length=254),
        ),
    ]
