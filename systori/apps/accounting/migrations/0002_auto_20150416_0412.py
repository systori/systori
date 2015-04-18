# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def add_transaction_group(apps, schema):
    TransactionGroup = apps.get_model('accounting', 'TransactionGroup')
    Transaction = apps.get_model('accounting', 'Transaction')
    Payment = apps.get_model('accounting', 'Payment')

    g1 = TransactionGroup.objects.create()
    t1 = Transaction.objects.get(id=1)
    t1.group = g1
    t1.save()
    t2 = Transaction.objects.get(id=2)
    t2.group = g1
    t2.save()
    Payment.objects.create(project_id=22, transaction_group=g1, amount=17850.00)

    g2 = TransactionGroup.objects.create()
    t1 = Transaction.objects.get(id=3)
    t1.group = g2
    t1.save()


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0001_initial'),
        ('project', '0009_project_account'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransactionGroup',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('date_recorded', models.DateTimeField(verbose_name='Date Recorded', auto_now_add=True)),
                ('notes', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='entry',
            options={'ordering': ['id']},
        ),
        migrations.AlterField(
            model_name='payment',
            name='is_discounted',
            field=models.BooleanField(verbose_name='Was discount applied?', default=False),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='payment',
            name='transaction',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='date_recorded',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='notes',
        ),
        migrations.AddField(
            model_name='entry',
            name='is_adjustment',
            field=models.BooleanField(verbose_name='Adjustment', default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='payment',
            name='transaction_group',
            field=models.OneToOneField(default=None, to='accounting.TransactionGroup', related_name='payment'),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name='payment',
            options={'ordering': ['id']},
        ),
        migrations.AddField(
            model_name='payment',
            name='project',
            field=models.ForeignKey(default=None, to='project.Project', related_name='payments'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transaction',
            name='group',
            field=models.ForeignKey(null=True, default=None, to='accounting.TransactionGroup', related_name='transactions'),
            preserve_default=False,
        ),
        #migrations.RunPython(add_transaction_group),
        migrations.AlterField(
            model_name='transaction',
            name='group',
            field=models.ForeignKey(default=None, to='accounting.TransactionGroup', related_name='transactions'),
            preserve_default=False,
        ),
    ]
