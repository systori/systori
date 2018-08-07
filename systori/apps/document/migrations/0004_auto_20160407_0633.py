# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("document", "0003_new_models")]

    operations = [
        migrations.AlterField(
            model_name="invoice",
            name="invoice_no",
            field=models.CharField(
                max_length=30, unique=True, verbose_name="Invoice No."
            ),
        )
    ]
