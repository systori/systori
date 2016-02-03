# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0008_refund'),
    ]

    operations = [
        migrations.AddField(
            model_name='letterhead',
            name='bottom_margin_next',
            field=models.DecimalField(default=Decimal('25'), decimal_places=2, max_digits=4, verbose_name='Bottom Margin Next'),
        ),
    ]
