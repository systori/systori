# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0007_remove_invoice_jobs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='json',
            field=jsonfield.fields.JSONField(),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='json',
            field=jsonfield.fields.JSONField(),
        ),
    ]
