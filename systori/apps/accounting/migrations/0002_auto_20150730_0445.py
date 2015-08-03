# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def add_cash_discount_account(apps, schema_editor):
    Account = apps.get_model('accounting', 'Account')
    from systori.apps.company.models import Company
    for company in Company.objects.all():
        company.activate()
        Account.objects.create(account_type="income", code="8736")


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0001_initial'),
        ('company', '0002_auto_20150706_0557')
    ]

    operations = [
        migrations.RunPython(add_cash_discount_account),
    ]
