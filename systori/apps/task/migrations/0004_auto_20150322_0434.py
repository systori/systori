# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('task', '0003_auto_20150211_1721'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='progressreport',
            options={'ordering': ['-timestamp'], 'verbose_name': 'Progress Report', 'verbose_name_plural': 'Progress Reports'},
        ),
        migrations.RemoveField(
            model_name='progressreport',
            name='date',
        ),
        migrations.AddField(
            model_name='progressreport',
            name='timestamp',
            field=models.DateTimeField(default=None, auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='progressreport',
            name='user',
            field=models.ForeignKey(related_name='filedreports', default=None, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='progressreport',
            name='task',
            field=models.ForeignKey(to='task.Task', related_name='progressreports'),
            preserve_default=True,
        ),
    ]
