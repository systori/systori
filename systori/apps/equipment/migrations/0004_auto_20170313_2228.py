# Generated by Django 2.0 on 2017-03-13 21:28

from django.db import migrations, models
import django.db.models.deletion
import systori.lib.fields


class Migration(migrations.Migration):

    dependencies = [("equipment", "0003_auto_20160901_2115")]

    operations = [
        migrations.CreateModel(
            name="EquipmentType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=512, verbose_name="Name")),
                (
                    "rate",
                    models.DecimalField(
                        decimal_places=2, max_digits=14, verbose_name="Rate"
                    ),
                ),
                (
                    "rate_type",
                    models.CharField(
                        choices=[
                            ("hourly", "Hourly"),
                            ("daily", "Daily"),
                            ("weekly", "Weekly"),
                            ("flat", "Flat Fee"),
                        ],
                        default="hourly",
                        max_length=128,
                        verbose_name="Rate Type",
                    ),
                ),
            ],
            bases=(models.Model, systori.lib.fields.RateType),
        ),
        migrations.AddField(
            model_name="equipment",
            name="equipment_type",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="equipment",
                to="equipment.EquipmentType",
            ),
        ),
    ]
