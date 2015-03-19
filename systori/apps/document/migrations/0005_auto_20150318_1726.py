# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import systori.apps.document.models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0003_auto_20150211_1721'),
        ('project', '0005_auto_20150318_1726'),
        ('document', '0004_invoice_invoice_no'),
    ]

    operations = [
        migrations.CreateModel(
            name='Evidence',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('notes', models.TextField(null=True, verbose_name='Notes', blank=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('document_date', models.DateField(default=datetime.date.today, verbose_name='Date', blank=True)),
                ('print_pdf', models.FileField(upload_to=systori.apps.document.models.generate_file_path)),
                ('print_latex', models.FileField(upload_to=systori.apps.document.models.generate_file_path)),
                ('json', models.FileField(upload_to=systori.apps.document.models.generate_file_path)),
                ('jobs', models.ManyToManyField(to='task.Job', related_name='evidences')),
                ('project', models.ForeignKey(related_name='evidences', to='project.Project')),
            ],
            options={
                'ordering': ['id'],
                'verbose_name': 'Invoice',
                'verbose_name_plural': 'Invoices',
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='documenttemplate',
            name='document_type',
            field=models.CharField(choices=[('proposal', 'Proposal'), ('invoice', 'Invoice'), ('evidence', 'Evidence')], default='proposal', verbose_name='Document Type', max_length=128),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='invoice',
            name='invoice_no',
            field=models.CharField(verbose_name='Invoice No.', max_length=30),
            preserve_default=True,
        ),
    ]
