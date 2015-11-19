# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations
from systori.apps.accounting.constants import TAX_RATE


def cleanup_json_and_stuff(apps, schema_editor):
    from systori.apps.company.models import Company

    for company in Company.objects.all():
        company.activate()
        Invoice = apps.get_model("document", "Invoice")
        for invoice in Invoice.objects.all():

            if 'debit_gross' not in invoice.json or\
                    (invoice.json['debit_gross'] == 0 and invoice.amount > 0):
                invoice.json['debit_gross'] = invoice.amount
                invoice.json['debit_net'] = round(invoice.amount / (1+TAX_RATE), 2)
                invoice.json['debit_tax'] = invoice.json['debit_gross'] - invoice.json['debit_net']
                invoice.save()

            if invoice.status == 'new':
                invoice.status = 'draft'
                invoice.save()


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0005_auto_20151119_1647'),
    ]

    operations = [
        migrations.RunPython(cleanup_json_and_stuff),
    ]
