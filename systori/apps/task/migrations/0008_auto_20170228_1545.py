# Generated by Django 2.0 on 2017-02-28 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("task", "0007_auto_20170201_0512")]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="variant_group",
            field=models.PositiveIntegerField(default=0),
        )
    ]
