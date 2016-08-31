# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-29 09:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def set_timetracking_letterhead(apps, schema_editor):
    from systori.apps.company.models import Company
    DocumentSettings = apps.get_model("document", "DocumentSettings")
    Letterhead = apps.get_model("document", "Letterhead")
    try:
        company = Company.objects.get(schema="mehr-handwerk")
    except Company.DoesNotExist:
        pass
    else:
        company.activate()
        settings = DocumentSettings.objects.first()
        settings.timetracking_letterhead = Letterhead.objects.get(id=2)
        settings.save()


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0005_auto_20160409_2219'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentsettings',
            name='timetracking_letterhead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='document.Letterhead'),
        ),
        migrations.RunPython(set_timetracking_letterhead),
    ]
