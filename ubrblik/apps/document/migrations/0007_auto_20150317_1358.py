# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0006_evidence'),
    ]

    operations = [
        migrations.RenameField(
            model_name='evidence',
            old_name='email_latex',
            new_name='latex',
        ),
        migrations.RenameField(
            model_name='evidence',
            old_name='email_pdf',
            new_name='pdf',
        ),
        migrations.RemoveField(
            model_name='evidence',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='evidence',
            name='footer',
        ),
        migrations.RemoveField(
            model_name='evidence',
            name='header',
        ),
        migrations.RemoveField(
            model_name='evidence',
            name='print_latex',
        ),
        migrations.RemoveField(
            model_name='evidence',
            name='print_pdf',
        ),
        migrations.AlterField(
            model_name='documenttemplate',
            name='document_type',
            field=models.CharField(choices=[('proposal', 'Proposal'), ('invoice', 'Invoice'), ('evidence', 'Evidence')], max_length=128, verbose_name='Document Type', default='proposal'),
            preserve_default=True,
        ),
    ]
