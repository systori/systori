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
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=512, verbose_name='Name')),
                ('letterhead_pdf', models.FileField(upload_to='letterhead', verbose_name='Letterhead PDF')),
                ('document_unit', models.CharField(max_length=5, default='mm', choices=[('mm', 'mm'), ('cm', 'cm'), ('inch', 'inch')], verbose_name='Document Unit')),
                ('top_margin', models.DecimalField(verbose_name='Top Margin', decimal_places=2, max_digits=4)),
                ('right_margin', models.DecimalField(verbose_name='Right Margin', decimal_places=2, max_digits=4)),
                ('bottom_margin', models.DecimalField(verbose_name='Bottom Margin', decimal_places=2, max_digits=4)),
                ('left_margin', models.DecimalField(verbose_name='Left Margin', decimal_places=2, max_digits=4)),
                ('top_margin_next', models.DecimalField(verbose_name='Top Margin Next', decimal_places=2, max_digits=4)),
                ('document_format', models.CharField(max_length=30, default='A4', choices=[('A6', 'A6'), ('A5', 'A5'), ('A4', 'A4'), ('A3', 'A3'), ('A2', 'A2'), ('A1', 'A1'), ('A0', 'A0'), ('LETTER', 'LETTER'), ('LEGAL', 'LEGAL'), ('ELEVENSEVENTEEN', 'ELEVENSEVENTEEN'), ('B6', 'B6'), ('B5', 'B5'), ('B4', 'B4'), ('B3', 'B3'), ('B2', 'B2'), ('B1', 'B1'), ('B0', 'B0')], verbose_name='Pagesize')),
                ('orientation', models.CharField(max_length=15, default='portrait', choices=[('portrait', 'Portrait'), ('landscape', 'Landscape')], verbose_name='Orientation')),
                ('debug', models.BooleanField(default=True, verbose_name='Debug Mode')),
            ],
        ),
    ]
