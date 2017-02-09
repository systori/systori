# Generated by Django 2.0 on 2017-02-09 04:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0008_rename_json_fields_invoice'),
    ]

    operations = [
        migrations.AddField(
            model_name='timesheet',
            name='holiday_expended',
            field=models.IntegerField(default=0, help_text='in seconds'),
        ),
        migrations.AddField(
            model_name='timesheet',
            name='holiday_new',
            field=models.IntegerField(default=0, help_text='in seconds'),
        ),
        migrations.AddField(
            model_name='timesheet',
            name='holiday_override',
            field=models.IntegerField(default=0, help_text='in seconds'),
        ),
        migrations.AddField(
            model_name='timesheet',
            name='holiday_override_notes',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='timesheet',
            name='holiday_transferred',
            field=models.IntegerField(default=0, help_text='in seconds'),
        ),
        migrations.AddField(
            model_name='timesheet',
            name='overtime_new',
            field=models.IntegerField(default=0, help_text='in seconds'),
        ),
        migrations.AddField(
            model_name='timesheet',
            name='overtime_override',
            field=models.IntegerField(default=0, help_text='in seconds'),
        ),
        migrations.AddField(
            model_name='timesheet',
            name='overtime_override_notes',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='timesheet',
            name='overtime_transferred',
            field=models.IntegerField(default=0, help_text='in seconds'),
        ),
    ]
