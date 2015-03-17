# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0007_auto_20150317_1358'),
    ]

    operations = [
        migrations.RenameField(
            model_name='evidence',
            old_name='latex',
            new_name='print_latex',
        ),
        migrations.RenameField(
            model_name='evidence',
            old_name='pdf',
            new_name='print_pdf',
        ),
    ]
