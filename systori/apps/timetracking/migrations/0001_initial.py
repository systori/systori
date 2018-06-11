# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Timer",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        verbose_name="ID",
                        serialize=False,
                        primary_key=True,
                    ),
                ),
                ("start", models.DateTimeField(db_index=True, auto_now_add=True)),
                ("end", models.DateTimeField(db_index=True, null=True, blank=True)),
                ("duration", models.IntegerField(default=0, help_text="in seconds")),
                (
                    "kind",
                    models.PositiveIntegerField(
                        default=10,
                        choices=[(10, "Work"), (20, "Holiday"), (30, "Illness")],
                        db_index=True,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "timers",
                "verbose_name": "timer",
                "ordering": ("start",),
            },
        )
    ]
