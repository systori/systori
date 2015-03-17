# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentTemplate',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(verbose_name='Name', max_length=512)),
                ('header', models.TextField(verbose_name='Header')),
                ('footer', models.TextField(verbose_name='Footer')),
                ('document_type', models.CharField(verbose_name='Document Type', default='proposal', choices=[('proposal', 'Proposal'), ('invoice', 'Invoice')], max_length=128)),
            ],
            options={
                'verbose_name': 'Document Template',
                'verbose_name_plural': 'Document Templates',
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
    ]
