# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0002_documenttemplate'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='document_date',
            field=models.DateField(blank=True, default=datetime.date.today, verbose_name='Date'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='proposal',
            name='document_date',
            field=models.DateField(blank=True, default=datetime.date.today, verbose_name='Date'),
            preserve_default=True,
        ),
    ]
