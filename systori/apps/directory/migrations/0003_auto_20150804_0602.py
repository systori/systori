# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms.models import model_to_dict
from django.db import models, migrations


def add_address_label(apps, schema_editor):
    Contact = apps.get_model('directory', 'Contact')
    from systori.apps.company.models import Company
    for company in Company.objects.all():
        company.activate()
        for contact in Contact.objects.all():
            contact.address_label = """\
            {business}
            z.H. {salutation} {first_name} {last_name}
            {address}
            {postal_code} {city}
            """.format(**model_to_dict(contact))
            contact.save()


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0002_auto_20150615_0046'),
        ('company', '0003_auto_20150730_2333')
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='address_label',
            field=models.TextField(verbose_name='Address Label', blank=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='is_address_label_generated',
            field=models.BooleanField(default=True),
        ),
        migrations.RunPython(add_address_label),
    ]
