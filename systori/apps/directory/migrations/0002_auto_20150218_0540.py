# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='country',
            field=models.CharField(verbose_name='Country', max_length=512, default='Deutschland'),
            preserve_default=True,
        ),
    ]
