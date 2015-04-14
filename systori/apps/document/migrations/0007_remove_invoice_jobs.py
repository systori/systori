# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0006_auto_20150402_0905'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='jobs',
        ),
    ]
