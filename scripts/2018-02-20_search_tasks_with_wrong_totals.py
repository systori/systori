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
counter_including_rounding_mismatch = 0
counter_real_mismatch = 0
counter_task_uses_equation = 0
counter_lineitem_uses_equation = 0
logging = {
    "task_uses_equation": [],
    "task_lineitem_equation": [],
    "task_mismatch": [],
    "task_real_mismatch": [],
}
for task in Task.objects.all():
    new_total = Decimal(0)
    if task.total_equation:
        counter_task_uses_equation += 1
        logging["task_uses_equation"].append(task.id)
    for li in task.lineitems.all():
        new_total += li.total
        if (
            (li.total_equation and is_formula(li.total_equation))
            or (li.qty_equation and is_formula(li.qty_equation))
            or (li.price_equation and is_formula(li.price_equation))
        ):
            counter_lineitem_uses_equation += 1
            logging["task_uses_equation"].append((task.id, li.id))
    if new_total != task.price:
        counter_including_rounding_mismatch += 1
        logging["task_mismatch"].append(task.id)
        if new_total - task.price > Decimal("0.01"):
            counter_real_mismatch += 1
            logging["task_real_mismatch"].append(
                (task.code, task.id, task.job.project.id, task.price, new_total)
            )

log_result = """
{} tasks are using equations.
{} lineitems are using equations.
{} tasks have a mismatch in task.price vs. sum of lineitems
{} tasks have a mismatch greater than 0.01
##### tasks to check manually
""".format(
    counter_task_uses_equation,
    counter_lineitem_uses_equation,
    counter_including_rounding_mismatch,
    counter_real_mismatch,
)
for entry in logging["task_real_mismatch"]:
    log_result += "Task {} (#{}) in project #{} ({} != {})\n".format(
        entry[0], entry[1], entry[2], entry[3], entry[4]
    )
print(log_result)
