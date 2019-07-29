#  WIP about finding time and material tasks within all companies and all tasks
#  will be the basis for the migration script, needs more testing

import os
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings.local")
import django
from django.db.models import Q

django.setup()

from systori.apps.company.models import Company
from systori.apps.task.models import Task


if __name__ == "__main__":
    counter = 0

    for c in Company.objects.all():
        c.activate()
        print(f"checking company {c.schema}")
        lineItems = []
        for task in Task.objects.filter(Q(qty__isnull=True) | Q(qty=Decimal("0"))):
            for li in task.lineitems.all():
                if "%" in li.unit:
                    print(li.task.job.project.id)
                    if li.id not in lineItems:
                        counter += 1
                        lineItems.append(li.id)
            # counter += task.lineitems.filter(unit="%").count()
        print(f"now we have {counter} with qty is None")
        print(f" lineItems had been {lineItems}")
    print("#### done ####\n\n")
