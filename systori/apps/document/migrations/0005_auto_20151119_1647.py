# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_fsm


def add_status_to_invoice_tx_in_json(apps, schema_editor):
    from systori.apps.company.models import Company

    for company in Company.objects.all():
        company.activate()
        Invoice = apps.get_model("document", "Invoice")
        for invoice in Invoice.objects.all():
            if 'transactions' in invoice.json:
                for tx in invoice.json['transactions']:
                    if tx['type'] in ('invoice', 'final-invoice'):
                        tx['invoice_status'] = 'paid'
                invoice.save()


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0004_auto_20151109_0632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='status',
            field=django_fsm.FSMField(default='draft', max_length=50, choices=[('draft', 'Draft'), ('sent', 'Sent'), ('paid', 'Paid')]),
        ),
        migrations.RunPython(add_status_to_invoice_tx_in_json),
    ]
