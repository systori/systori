# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0005_job_account'),
        ('accounting', '0004_auto_20151013_0730'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='entry',
            options={'ordering': ['transaction__transacted_on', 'id']},
        ),
        migrations.AddField(
            model_name='entry',
            name='job',
            field=models.ForeignKey(to='task.Job', null=True, related_name='+'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(max_length=32, null=True, choices=[('invoice', 'Invoice'), ('final-invoice', 'Final Invoice'), ('payment', 'Payment')], verbose_name='Transaction Type'),
        ),
    ]
