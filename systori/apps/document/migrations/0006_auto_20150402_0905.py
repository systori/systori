# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0005_auto_20150318_1726'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='latex_template',
            field=models.CharField(max_length=512, default='invoice.tex', verbose_name='Template'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='proposal',
            name='latex_template',
            field=models.CharField(max_length=512, default='proposal.tex', verbose_name='Template'),
            preserve_default=True,
        ),
    ]
