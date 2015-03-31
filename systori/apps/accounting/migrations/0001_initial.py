# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0008_dailyplan_equipment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('project', models.OneToOneField(serialize=False, to='project.Project', primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('amount', models.DecimalField(verbose_name='Amount', default=0.0, decimal_places=4, max_digits=14)),
                ('account', models.ForeignKey(to='accounting.Account', related_name='entries')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('date_sent', models.DateField(verbose_name='Date Sent', default=datetime.date.today)),
                ('date_received', models.DateField(verbose_name='Date Received', default=datetime.date.today)),
                ('date_recorded', models.DateTimeField(auto_now_add=True, verbose_name='Date Recorded')),
                ('amount', models.DecimalField(verbose_name='Amount', default=0.0, decimal_places=4, max_digits=14)),
                ('notes', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='entry',
            name='transaction',
            field=models.ForeignKey(to='accounting.Transaction', related_name='entries'),
            preserve_default=True,
        ),
    ]
