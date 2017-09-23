# Generated by Django 2.0 on 2017-09-22 18:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('company', '0011_remove_worker_is_timetracking_enabled'),
        ('project', '0007_auto_20170915_1537'),
        ('document', '0014_auto_20170915_0609'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ('current__uploaded',),
            },
        ),
        migrations.CreateModel(
            name='FileAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(max_length=512, upload_to='attachments', verbose_name='File')),
                ('uploaded', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('attachment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='document.Attachment')),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='company.Worker')),
            ],
            options={
                'ordering': ('uploaded',),
            },
        ),
        migrations.AddField(
            model_name='attachment',
            name='current',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='document.FileAttachment'),
        ),
        migrations.AddField(
            model_name='attachment',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='project.Project'),
        ),
    ]
