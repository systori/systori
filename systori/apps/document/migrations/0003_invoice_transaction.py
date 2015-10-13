# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0003_auto_20151013_0615'),
        ('document', '0002_auto_20150615_0046'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='transaction',
            field=models.ForeignKey(to='accounting.Transaction', null=True, related_name='invoice'),
        ),
    ]
