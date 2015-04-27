# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0007_remove_invoice_jobs'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='evidence',
            name='jobs',
        ),
        migrations.RemoveField(
            model_name='evidence',
            name='project',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='email_latex',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='email_pdf',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='footer',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='header',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='latex_template',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='print_latex',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='print_pdf',
        ),
        migrations.RemoveField(
            model_name='proposal',
            name='email_latex',
        ),
        migrations.RemoveField(
            model_name='proposal',
            name='email_pdf',
        ),
        migrations.RemoveField(
            model_name='proposal',
            name='footer',
        ),
        migrations.RemoveField(
            model_name='proposal',
            name='header',
        ),
        migrations.RemoveField(
            model_name='proposal',
            name='latex_template',
        ),
        migrations.RemoveField(
            model_name='proposal',
            name='print_latex',
        ),
        migrations.RemoveField(
            model_name='proposal',
            name='print_pdf',
        ),
        migrations.AddField(
            model_name='invoice',
            name='json_version',
            field=models.CharField(max_length=5, default='1.0'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='proposal',
            name='json_version',
            field=models.CharField(max_length=5, default='1.0'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='documenttemplate',
            name='document_type',
            field=models.CharField(max_length=128, verbose_name='Document Type', default='proposal', choices=[('proposal', 'Proposal'), ('invoice', 'Invoice')]),
        ),
        migrations.DeleteModel(
            name='Evidence',
        ),

        migrations.RemoveField(
            model_name='invoice',
            name='json',
        ),
        migrations.RemoveField(
            model_name='proposal',
            name='json',
        ),

        migrations.AddField(
            model_name='invoice',
            name='json',
            field=jsonfield.fields.JSONField(default={}),
        ),
        migrations.AddField(
            model_name='proposal',
            name='json',
            field=jsonfield.fields.JSONField(default={}),
        ),

    ]
