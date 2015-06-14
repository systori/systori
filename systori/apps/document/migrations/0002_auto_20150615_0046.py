# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0001_initial'),
        ('project', '0001_initial'),
        ('document', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='jobs',
            field=models.ManyToManyField(verbose_name='Jobs', to='task.Job', related_name='proposals'),
        ),
        migrations.AddField(
            model_name='proposal',
            name='project',
            field=models.ForeignKey(to='project.Project', related_name='proposals'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='project',
            field=models.ForeignKey(to='project.Project', related_name='invoices'),
        ),
    ]
