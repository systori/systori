# Generated by Django 2.0 on 2017-09-21 15:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='note',
            options={'ordering': ('created',)},
        ),
    ]
