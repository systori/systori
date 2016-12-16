# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(verbose_name='Name', max_length=255)),
                ('manufacturer', models.CharField(verbose_name='Manufacturer', max_length=255)),
                ('purchase_date', models.DateField(blank=True, verbose_name='Purchase Date', null=True)),
                ('purchase_price', models.DecimalField(decimal_places=2, verbose_name='Purchase Price', default=0.0, max_digits=14)),
            ],
        ),
    ]
