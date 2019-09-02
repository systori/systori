# Generated by Django 2.2.4 on 2019-08-30 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("document", "0002_auto_20190730_2210")]

    operations = [
        migrations.AlterField(
            model_name="documentsettings",
            name="language",
            field=models.CharField(
                choices=[("de", "Deutsch"), ("en", "English")],
                default="de",
                max_length=2,
                unique=True,
                verbose_name="language",
            ),
        )
    ]
