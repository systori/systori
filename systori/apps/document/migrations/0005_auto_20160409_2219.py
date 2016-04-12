# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-04-09 20:19
from __future__ import unicode_literals

from django.db import migrations


def migrate_document_date(apps, schema_editor):
    from systori.apps.company.models import Company
    from systori.apps.document.models import Invoice, Adjustment, Payment, Refund, Proposal

    for company in Company.objects.all():
        company.activate()

        for doc_class in [Invoice, Adjustment, Payment, Refund, Proposal]:
            for doc in doc_class.objects.all():
                doc.json['document_date'] = doc.document_date
                doc.save()


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0004_auto_20160407_0633'),
    ]

    operations = [
        migrations.RunPython(migrate_document_date)
    ]
