# Generated by Django 2.0 on 2017-03-05 13:58

from django.db import migrations, models
from postgres_schema.operations import RunInSchemas


def update_timers(apps, schema_editor):

    from systori.apps.timetracking.models import Timer

    for timer in Timer.objects.all():
        if timer.kind == "holiday":
            timer.kind = "vacation"
        elif timer.kind == "training":
            timer.kind = "work"
        elif timer.kind == "illness":
            timer.kind = "sick"
        timer.duration = timer.running_duration
        timer.save()

    from systori.apps.document.models import Timesheet

    for ts in Timesheet.objects.all():
        ts.json["work_correction"] = int(ts.json["work_correction"] // 60)
        ts.json["overtime_correction"] = int(ts.json["overtime_correction"] // 60)
        ts.json["vacation_correction"] = int(ts.json["holiday_correction"] // 60)
        ts.json["vacation_correction_notes"] = ts.json["holiday_correction_notes"]
        ts.calculate()
        ts.save()


class Migration(migrations.Migration):

    dependencies = [
        ("timetracking", "0012_auto_20170201_1525"),
        ("document", "0010_auto_20170214_0028"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="timer",
            options={
                "ordering": ("started",),
                "verbose_name": "timer",
                "verbose_name_plural": "timers",
            },
        ),
        migrations.RenameField(
            model_name="timer", old_name="end_latitude", new_name="ending_latitude"
        ),
        migrations.RenameField(
            model_name="timer", old_name="end_longitude", new_name="ending_longitude"
        ),
        migrations.RenameField(
            model_name="timer", old_name="start_latitude", new_name="starting_latitude"
        ),
        migrations.RenameField(
            model_name="timer",
            old_name="start_longitude",
            new_name="starting_longitude",
        ),
        migrations.AlterField(
            model_name="timer", name="start", field=models.DateTimeField(db_index=True)
        ),
        migrations.RenameField(
            model_name="timer", old_name="start", new_name="started"
        ),
        migrations.RenameField(model_name="timer", old_name="end", new_name="stopped"),
        migrations.RemoveField(model_name="timer", name="date"),
        migrations.AlterField(
            model_name="timer",
            name="duration",
            field=models.IntegerField(default=0, help_text="in minutes"),
        ),
        migrations.AlterField(
            model_name="timer",
            name="kind",
            field=models.CharField(
                choices=[
                    ("work", "Work"),
                    ("vacation", "Vacation"),
                    ("sick", "Sick"),
                    ("public_holiday", "Public holiday"),
                    ("paid_leave", "Paid leave"),
                    ("unpaid_leave", "Unpaid leave"),
                ],
                db_index=True,
                default="work",
                max_length=32,
            ),
        ),
        RunInSchemas(migrations.RunPython(update_timers)),
    ]