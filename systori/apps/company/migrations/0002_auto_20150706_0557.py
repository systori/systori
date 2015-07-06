# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='access',
            name='is_active',
            field=models.BooleanField(help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', default=True, verbose_name='active'),
        ),
        migrations.AddField(
            model_name='access',
            name='is_foreman',
            field=models.BooleanField(help_text='Foremen can manage laborers.', default=False, verbose_name='Foreman'),
        ),
        migrations.AddField(
            model_name='access',
            name='is_laborer',
            field=models.BooleanField(help_text='Laborer has limited access to the system.', default=True, verbose_name='Laborer'),
        ),
        migrations.AddField(
            model_name='access',
            name='is_staff',
            field=models.BooleanField(help_text='Designates whether the user can log into this admin site.', default=False, verbose_name='staff status'),
        ),
        migrations.AlterField(
            model_name='access',
            name='is_accountant',
            field=models.BooleanField(default=False, verbose_name='accountant'),
        ),
        migrations.AlterUniqueTogether(
            name='access',
            unique_together=set([('company', 'user')]),
        ),
        migrations.RemoveField(
            model_name='access',
            name='is_employee',
        ),
        migrations.RemoveField(
            model_name='access',
            name='is_enabled',
        ),
    ]
