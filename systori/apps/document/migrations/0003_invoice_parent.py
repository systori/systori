# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0003_auto_20151030_1121'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='parent',
            field=models.ForeignKey(related_name='invoices', to='document.Invoice', null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='transaction',
            field=models.OneToOneField(related_name='invoice', null=True, on_delete=models.deletion.SET_NULL, to='accounting.Transaction'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='status',
            field=django_fsm.FSMField(max_length=50, choices=[('draft', 'Draft'), ('sent', 'Sent')], default='draft'),
        ),
    ]
