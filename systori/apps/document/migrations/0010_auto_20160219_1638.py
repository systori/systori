# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0009_letterhead_bottom_margin_next'),
    ]

    operations = [
        migrations.AddField(
            model_name='letterhead',
            name='font',
            field=models.CharField(default='OpenSans', choices=[('OpenSans', 'Open Sans'), ('DroidSerif', 'Droid Serif'), ('Tinos', 'Tinos')], max_length=15, verbose_name='Font'),
        ),
        migrations.AlterField(
            model_name='letterhead',
            name='bottom_margin',
            field=models.DecimalField(default=Decimal('25'), max_digits=5, decimal_places=2, verbose_name='Bottom Margin'),
        ),
        migrations.AlterField(
            model_name='letterhead',
            name='bottom_margin_next',
            field=models.DecimalField(default=Decimal('25'), max_digits=5, decimal_places=2, verbose_name='Bottom Margin Next'),
        ),
        migrations.AlterField(
            model_name='letterhead',
            name='left_margin',
            field=models.DecimalField(default=Decimal('25'), max_digits=5, decimal_places=2, verbose_name='Left Margin'),
        ),
        migrations.AlterField(
            model_name='letterhead',
            name='right_margin',
            field=models.DecimalField(default=Decimal('25'), max_digits=5, decimal_places=2, verbose_name='Right Margin'),
        ),
        migrations.AlterField(
            model_name='letterhead',
            name='top_margin',
            field=models.DecimalField(default=Decimal('25'), max_digits=5, decimal_places=2, verbose_name='Top Margin'),
        ),
        migrations.AlterField(
            model_name='letterhead',
            name='top_margin_next',
            field=models.DecimalField(default=Decimal('25'), max_digits=5, decimal_places=2, verbose_name='Top Margin Next'),
        ),
    ]
