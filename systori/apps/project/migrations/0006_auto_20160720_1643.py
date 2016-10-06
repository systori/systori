# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-20 14:43
from django.db import migrations, models
import django.db.models.deletion


def zfill_field_renamed(apps, schema_editor):
    from systori.apps.company.models import Company
    Project = apps.get_model("project", "Project")
    for company in Company.objects.all():
        company.activate()
        for project in Project.objects.all():
            project.level_1_zfill = project.job_zfill
            project.level_2_zfill = project.taskgroup_zfill


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0005_jobsite_travel_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='has_level_2',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='project',
            name='has_level_3',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='project',
            name='has_level_4',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='project',
            name='has_level_5',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='project',
            name='level_1_zfill',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Level 1 Zero Fill'),
        ),
        migrations.AddField(
            model_name='project',
            name='level_2_name',
            field=models.CharField(default='Main Section', max_length=512, verbose_name='Level 2 Name'),
        ),
        migrations.AddField(
            model_name='project',
            name='level_2_zfill',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Level 2 Zero Fill'),
        ),
        migrations.AddField(
            model_name='project',
            name='level_3_name',
            field=models.CharField(default='Section', max_length=512, verbose_name='Level 3 Name'),
        ),
        migrations.AddField(
            model_name='project',
            name='level_3_zfill',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Level 3 Zero Fill'),
        ),
        migrations.AddField(
            model_name='project',
            name='level_4_name',
            field=models.CharField(default='Sub-Section', max_length=512, verbose_name='Level 4 Name'),
        ),
        migrations.AddField(
            model_name='project',
            name='level_4_zfill',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Level 4 Zero Fill'),
        ),
        migrations.AddField(
            model_name='project',
            name='level_5_name',
            field=models.CharField(default='Title', max_length=512, verbose_name='Level 5 Name'),
        ),
        migrations.AddField(
            model_name='project',
            name='level_5_zfill',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Level 5 Zero Fill'),
        ),
        migrations.RunPython(zfill_field_renamed),
        migrations.RemoveField(
            model_name='project',
            name='job_zfill',
        ),
        migrations.RemoveField(
            model_name='project',
            name='taskgroup_zfill',
        ),
        migrations.AlterModelOptions(
            name='teammember',
            options={'ordering': ['-is_foreman', 'worker__user__first_name']},
        ),
        migrations.RenameField(
            model_name='dailyplan',
            old_name='accesses',
            new_name='workers',
        ),
        migrations.RenameField(
            model_name='teammember',
            old_name='access',
            new_name='worker',
        ),
        migrations.AlterField(
            model_name='teammember',
            name='dailyplan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='project.DailyPlan'),
        ),
    ]
