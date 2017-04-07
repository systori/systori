from django.db import migrations
from postgres_schema.operations import RunInSchemas


def migrate_json(apps, schema_editor):
    from systori.apps.document.models import Invoice, Proposal
    for invoice in Invoice.objects.all():
        invoice.json['project_id'] = invoice.project_id
        invoice.json['show_project_id'] = False
        invoice.save()
    for proposal in Proposal.objects.all():
        proposal.json['project_id'] = proposal.project_id
        proposal.json['show_project_id'] = False
        proposal.save()


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0011_auto_20170404_2058'),
    ]

    operations = [
        RunInSchemas(migrations.RunPython(migrate_json)),
    ]
