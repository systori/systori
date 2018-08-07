# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("timetracking", "0002_auto_20160322_1908"),
    ]

    operations = [
        migrations.AddField(
            model_name="timer",
            name="altered_by",
            field=models.ForeignKey(
                null=True,
                blank=True,
                to=settings.AUTH_USER_MODEL,
                related_name="timers_altered",
                on_delete=models.SET_NULL,
            ),
        )
    ]
