# import django; django.setup()
from django.db import migrations


def migrate_json(apps, schema_editor):
    from systori.apps.company.models import Company
    from systori.apps.document.models import Invoice
    from systori.apps.document.models import Proposal

    for company in Company.objects.all():
        company.activate()
        for invoice in Invoice.objects.all():
            jobs = invoice.json.get("jobs", [])
            for job in jobs:
                job["description"] = ""
                job["groups"] = job.pop("taskgroups")
                job["tasks"] = []
                for group in job["groups"]:
                    group["group.id"] = group.pop("id", None)
                    group["progress"] = group.pop("total")
                    group["estimate"] = None  # NOTE: not available
                    group["groups"] = []
                    for task in group["tasks"]:
                        task["task.id"] = task.pop("id", None)
                        task["is_provisional"] = False
                        task["variant_group"] = None
                        task["variant_serial"] = 0
                        task["qty"] = None  # NOTE: not available
                        task["progress"] = task.pop("total")
                        task["estimate"] = None  # NOTE: not available
                        for lineitem in task["lineitems"]:
                            lineitem["lineitem.id"] = lineitem.pop("id", None)
                            lineitem["estimate"] = lineitem.pop("price_per")
            invoice.save()

        for proposal in Proposal.objects.all():
            jobs = proposal.json.get("jobs", [])
            for job in jobs:
                job["description"] = ""
                job["groups"] = job.pop("taskgroups")
                job["tasks"] = []
                for group in job["groups"]:
                    group["group.id"] = group.pop("id", None)
                    group["estimate"] = group.pop("estimate_net")
                    group["groups"] = []
                    for task in group["tasks"]:
                        task["task.id"] = task.pop("id", None)
                        task["is_provisional"] = task.pop("is_optional")
                        task["variant_group"] = None
                        task["variant_serial"] = 0
                        task["estimate"] = task.pop("estimate_net")
                        for lineitem in task["lineitems"]:
                            lineitem["lineitem.id"] = lineitem.pop("id", None)
                            lineitem["estimate"] = lineitem.pop("price_per")
            proposal.save()


# migrate_json(None, None)


class Migration(migrations.Migration):

    dependencies = [
        ("document", "0007_auto_20160906_1650"),
        ("project", "0006_auto_20160720_1643"),
    ]

    operations = [migrations.RunPython(migrate_json)]
