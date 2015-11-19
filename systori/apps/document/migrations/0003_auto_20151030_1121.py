# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from decimal import Decimal
from datetime import date


def create_letterhead_and_update_documents(apps, schema_editor):
    from systori.apps.company.models import Company
    Letterhead = apps.get_model("document", "Letterhead")
    Proposal = apps.get_model("document", "Proposal")
    Invoice = apps.get_model("document", "Invoice")

    letterhead = Letterhead()
    letterhead.name = "auto-generated {}".format(date.today())
    for company in Company.objects.all():
        company.activate()
        # force django to disconnect the letterhead object from the db
        letterhead.id = None
        letterhead.save()
        for invoice in Invoice.objects.all():
            invoice.letterhead = letterhead
            invoice.save()
        for proposal in Proposal.objects.all():
            proposal.letterhead = letterhead
            proposal.save()


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0002_auto_20150615_0046'),
    ]

    operations = [
        migrations.CreateModel(
            name='Letterhead',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='Name', max_length=512)),
                ('letterhead_pdf', models.FileField(verbose_name='Letterhead PDF', upload_to='letterhead')),
                ('document_unit', models.CharField(verbose_name='Document Unit', max_length=5, default='mm', choices=[('mm', 'mm'), ('cm', 'cm'), ('inch', 'inch')])),
                ('top_margin', models.DecimalField(decimal_places=2, max_digits=4, verbose_name='Top Margin')),
                ('right_margin', models.DecimalField(decimal_places=2, max_digits=4, verbose_name='Right Margin')),
                ('bottom_margin', models.DecimalField(decimal_places=2, max_digits=4, verbose_name='Bottom Margin')),
                ('left_margin', models.DecimalField(decimal_places=2, max_digits=4, verbose_name='Left Margin')),
                ('top_margin_next', models.DecimalField(decimal_places=2, max_digits=4, verbose_name='Top Margin Next')),
                ('document_format', models.CharField(verbose_name='Pagesize', max_length=30, default='A4', choices=[('A5', 'A5'), ('A4', 'A4'), ('A3', 'A3'), ('LETTER', 'LETTER'), ('LEGAL', 'LEGAL'), ('ELEVENSEVENTEEN', 'ELEVENSEVENTEEN'), ('B5', 'B5'), ('B4', 'B4')])),
                ('orientation', models.CharField(verbose_name='Orientation', max_length=15, default='portrait', choices=[('portrait', 'Portrait'), ('landscape', 'Landscape')])),
                ('debug', models.BooleanField(default=True, verbose_name='Debug Mode')),
            ],
        ),
        migrations.CreateModel(
            name='DocumentSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('language', models.CharField(verbose_name='language', unique=True, max_length=2, default='de', choices=[('de', 'Deutsch'), ('en', 'English')])),
            ],
        ),
        migrations.AddField(
            model_name='documentsettings',
            name='evidence_letterhead',
            field=models.ForeignKey(to='document.Letterhead', related_name='+', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True),
        ),
        migrations.AddField(
            model_name='documentsettings',
            name='invoice_letterhead',
            field=models.ForeignKey(to='document.Letterhead', related_name='+', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True),
        ),
        migrations.AddField(
            model_name='documentsettings',
            name='invoice_text',
            field=models.ForeignKey(to='document.DocumentTemplate', related_name='+', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True),
        ),
        migrations.AddField(
            model_name='documentsettings',
            name='itemized_letterhead',
            field=models.ForeignKey(to='document.Letterhead', related_name='+', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True),
        ),
        migrations.AddField(
            model_name='documentsettings',
            name='proposal_letterhead',
            field=models.ForeignKey(to='document.Letterhead', related_name='+', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True),
        ),
        migrations.AddField(
            model_name='documentsettings',
            name='proposal_text',
            field=models.ForeignKey(to='document.DocumentTemplate', related_name='+', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True),
        ),
        migrations.AlterField(
            model_name='letterhead',
            name='bottom_margin',
            field=models.DecimalField(decimal_places=2, max_digits=4, default=Decimal('25'), verbose_name='Bottom Margin'),
        ),
        migrations.AlterField(
            model_name='letterhead',
            name='left_margin',
            field=models.DecimalField(decimal_places=2, max_digits=4, default=Decimal('25'), verbose_name='Left Margin'),
        ),
        migrations.AlterField(
            model_name='letterhead',
            name='right_margin',
            field=models.DecimalField(decimal_places=2, max_digits=4, default=Decimal('25'), verbose_name='Right Margin'),
        ),
        migrations.AlterField(
            model_name='letterhead',
            name='top_margin',
            field=models.DecimalField(decimal_places=2, max_digits=4, default=Decimal('25'), verbose_name='Top Margin'),
        ),
        migrations.AlterField(
            model_name='letterhead',
            name='top_margin_next',
            field=models.DecimalField(decimal_places=2, max_digits=4, default=Decimal('25'), verbose_name='Top Margin Next'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='letterhead',
            field=models.ForeignKey(to='document.Letterhead', null=True, related_name='invoice_documents'),
        ),
        migrations.AddField(
            model_name='proposal',
            name='letterhead',
            field=models.ForeignKey(to='document.Letterhead', null=True, related_name='proposal_documents'),
        ),
        migrations.RunPython(create_letterhead_and_update_documents),
        migrations.AlterField(
            model_name='invoice',
            name='letterhead',
            field=models.ForeignKey(related_name='invoice_documents', to='document.Letterhead'),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='letterhead',
            field=models.ForeignKey(related_name='proposal_documents', to='document.Letterhead'),
        ),
    ]
