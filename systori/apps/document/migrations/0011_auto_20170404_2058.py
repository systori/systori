from django.db import migrations
from postgres_schema.operations import RunInSchemas


def migrate_json(apps, schema_editor):
    from systori.apps.document.models import Invoice
    for invoice in Invoice.objects.all():
        invoice.json['vesting_start'] = None
        invoice.json['vesting_end'] = None
        invoice.save()


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0010_auto_20170214_0028'),
    ]

    operations = [
        RunInSchemas(migrations.RunPython(migrate_json)),
    ]
