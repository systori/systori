# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Estimate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('is_template', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Estimate',
                'verbose_name_plural': 'Estimates',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LineItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('estimate', models.ForeignKey(related_name='lineitems', to='proposal.Estimate')),
            ],
            options={
                'verbose_name': 'Line Item',
                'verbose_name_plural': 'Line Items',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LineItemType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='Name', max_length=128)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('description', models.TextField(verbose_name='Proposal Description', blank=True, null=True)),
                ('project', models.ForeignKey(related_name='proposals', to='project.Project')),
            ],
            options={
                'verbose_name': 'Proposal',
                'verbose_name_plural': 'Proposals',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='Name', max_length=128)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='lineitem',
            name='itemtype',
            field=models.ForeignKey(to='proposal.LineItemType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='lineitem',
            name='unit',
            field=models.ForeignKey(to='proposal.Unit'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='estimate',
            name='proposal',
            field=models.ForeignKey(related_name='estimates', to='proposal.Proposal'),
            preserve_default=True,
        ),
    ]
