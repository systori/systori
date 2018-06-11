import os
import unicodedata
import json
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
django.setup()

from systori.lib.accounting.tools import JSONEncoder
from systori.apps.accounting.models import create_account_for_job
from systori.apps.company.models import Company
from systori.apps.project.models import Project
from systori.apps.task.models import Task, Group, Job, LineItem
from systori.apps.task.templatetags.task import is_formula
from decimal import Decimal


# for company in Company.objects.all():
#     company.activate()
#     print(company.name)
Company.objects.get(schema="mehr-handwerk").activate()

task_counter = Task.objects.count()
counter = 0
for task in Task.objects.all():
    if task.qty and task.complete >= task.qty * Decimal(1.5):
        counter += 1
        print(
            "PosID {} angeboten {} abgerechnet {} -> {:.2f}%".format(
                task.id, task.qty, task.complete, task.complete / task.qty * 100
            )
        )
print(
    "Von insgesamt {} sind {} Pos. über 150% abgerechnet, also knapp {:.2f}%".format(
        task_counter, counter, counter / task_counter * 100
    )
)
