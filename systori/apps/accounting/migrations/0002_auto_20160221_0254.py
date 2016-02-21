# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0001_initial'),
        ('task', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='job',
            field=models.ForeignKey(to='task.Job', related_name='+', null=True),
        ),
        migrations.AddField(
            model_name='entry',
            name='transaction',
            field=models.ForeignKey(to='accounting.Transaction', related_name='entries'),
        ),
    ]
