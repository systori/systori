# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0003_auto_20150804_0602'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contact',
            options={'verbose_name': 'Contact', 'verbose_name_plural': 'Contacts', 'ordering': ['first_name', 'last_name']},
        ),
        migrations.AlterField(
            model_name='contact',
            name='is_address_label_generated',
            field=models.BooleanField(default=True, verbose_name='auto-generate address label'),
        ),
    ]
