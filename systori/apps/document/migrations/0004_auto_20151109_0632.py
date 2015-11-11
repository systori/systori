# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0003_invoice_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='amount',
            field=models.DecimalField(decimal_places=2, verbose_name='Amount', max_digits=12, default=0.0),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='amount',
            field=models.DecimalField(decimal_places=2, verbose_name='Amount', max_digits=12, default=0.0),
        ),
    ]
