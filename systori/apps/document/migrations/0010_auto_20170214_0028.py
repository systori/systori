# Generated by Django 2.0 on 2017-02-13 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0009_auto_20170213_2355'),
    ]

    operations = [
        migrations.AlterField(
            model_name='letterhead',
            name='font',
            field=models.CharField(choices=[('OpenSans', 'OpenSans'), ('DroidSerif', 'DroidSerif'), ('Tinos', 'Tinos'), ('Ubuntu', 'Ubuntu')], default='OpenSans', max_length=15, verbose_name='Font'),
        ),
    ]