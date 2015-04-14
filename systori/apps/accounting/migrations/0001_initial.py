# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('account_type', models.CharField(max_length=128, verbose_name='Account Type', choices=[('asset', 'Asset'), ('liability', 'Liability'), ('income', 'Income'), ('expense', 'Expense')])),
                ('code', models.CharField(max_length=32, verbose_name='Code')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('date_recorded', models.DateTimeField(verbose_name='Date Recorded', auto_now_add=True)),
                ('notes', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('amount', models.DecimalField(verbose_name='Amount', max_digits=14, default=0.0, decimal_places=4)),
                ('account', models.ForeignKey(related_name='entries', to='accounting.Account')),
                ('transaction', models.ForeignKey(related_name='entries', to='accounting.Transaction')),
                ('is_discount', models.BooleanField(verbose_name='Discount', default=False))
            ],
            options={
                'ordering': ['transaction__date_recorded'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('amount', models.DecimalField(verbose_name='Amount', max_digits=14, default=0.0, decimal_places=4)),
                ('date_sent', models.DateField(verbose_name='Date Sent', default=datetime.date.today)),
                ('date_received', models.DateField(verbose_name='Date Received', default=datetime.date.today)),
                ('is_discounted', models.BooleanField(verbose_name='Was discounted applied?', default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='payment',
            name='transaction',
            field=models.ForeignKey(related_name='payments', to='accounting.Transaction'),
            preserve_default=True,
        ),
    ]
