# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0002_auto_20150615_0046'),
    ]

    operations = [
        migrations.CreateModel(
            name='Letterhead',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(verbose_name='Name', max_length=512)),
                ('document_unit', models.CharField(default='mm', choices=[('mm', 'mm'), ('cm', 'cm')], verbose_name='Document Unit', max_length=5)),
                ('top_margin', models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Top Margin')),
                ('right_margin', models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Right Margin')),
                ('bottom_margin', models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Bottom Margin')),
                ('left_margin', models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Left Margin')),
                ('letterhead_pdf', models.FileField(verbose_name='Letterhead PDF', upload_to='letterhead')),
                ('document_format', models.CharField(default='A4', choices=[('A4', 'A4')], verbose_name='Pagesize', max_length=30)),
                ('orientation', models.CharField(default='portrait', choices=[('portrait', 'Portrait'), ('landscape', 'Landscape')], verbose_name='Orientation', max_length=15)),
            ],
        ),
    ]
