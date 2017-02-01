# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
        ('task', '0001_initial'),
        ('document', '0001_initial'),
        ('accounting', '0002_auto_20160221_0254'),
    ]

    operations = [
        migrations.AddField(
            model_name='refund',
            name='project',
            field=models.ForeignKey(to='project.Project', related_name='refunds', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='refund',
            name='transaction',
            field=models.OneToOneField(to='accounting.Transaction', on_delete=django.db.models.deletion.SET_NULL, related_name='refund', null=True),
        ),
        migrations.AddField(
            model_name='proposal',
            name='jobs',
            field=models.ManyToManyField(verbose_name='Jobs', to='task.Job', related_name='proposals'),
        ),
        migrations.AddField(
            model_name='proposal',
            name='letterhead',
            field=models.ForeignKey(to='document.Letterhead', related_name='proposal_documents', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='proposal',
            name='project',
            field=models.ForeignKey(to='project.Project', related_name='proposals', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='invoice',
            name='letterhead',
            field=models.ForeignKey(to='document.Letterhead', related_name='invoice_documents', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='invoice',
            name='parent',
            field=models.ForeignKey(to='document.Invoice', related_name='invoices', null=True, on_delete=models.SET_NULL),
        ),
        migrations.AddField(
            model_name='invoice',
            name='project',
            field=models.ForeignKey(to='project.Project', related_name='invoices', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='invoice',
            name='transaction',
            field=models.OneToOneField(to='accounting.Transaction', on_delete=django.db.models.deletion.SET_NULL, related_name='invoice', null=True),
        ),
        migrations.AddField(
            model_name='documentsettings',
            name='evidence_letterhead',
            field=models.ForeignKey(to='document.Letterhead', on_delete=django.db.models.deletion.SET_NULL, blank=True, null=True, related_name='+'),
        ),
        migrations.AddField(
            model_name='documentsettings',
            name='invoice_letterhead',
            field=models.ForeignKey(to='document.Letterhead', on_delete=django.db.models.deletion.SET_NULL, blank=True, null=True, related_name='+'),
        ),
        migrations.AddField(
            model_name='documentsettings',
            name='invoice_text',
            field=models.ForeignKey(to='document.DocumentTemplate', on_delete=django.db.models.deletion.SET_NULL, blank=True, null=True, related_name='+'),
        ),
        migrations.AddField(
            model_name='documentsettings',
            name='itemized_letterhead',
            field=models.ForeignKey(to='document.Letterhead', on_delete=django.db.models.deletion.SET_NULL, blank=True, null=True, related_name='+'),
        ),
        migrations.AddField(
            model_name='documentsettings',
            name='proposal_letterhead',
            field=models.ForeignKey(to='document.Letterhead', on_delete=django.db.models.deletion.SET_NULL, blank=True, null=True, related_name='+'),
        ),
        migrations.AddField(
            model_name='documentsettings',
            name='proposal_text',
            field=models.ForeignKey(to='document.DocumentTemplate', on_delete=django.db.models.deletion.SET_NULL, blank=True, null=True, related_name='+'),
        ),
    ]
