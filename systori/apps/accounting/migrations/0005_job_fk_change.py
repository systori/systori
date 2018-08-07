# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounting", "0004_auto_20160412_1641"),
        ("task", "0004_data_migration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="entry",
            name="job",
            field=models.ForeignKey(
                "task.Job", models.SET_NULL, related_name="+", null=True
            ),
        )
    ]
