import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
import django
django.setup()

import json
from decimal import Decimal
from systori.apps.company.models import Company
from systori.apps.task.models import Task, LineItem, ProgressReport

Company.objects.get(schema='mehr-handwerk').activate()

with open('qty.json') as f:
    data = json.load(f)
    for li in data['lineitems']:
        lineitem = LineItem.objects.get(pk=li[0])
        lineitem.qty = Decimal(li[1])
        lineitem.save()
    for ta in data['tasks']:
        task = Task.objects.get(pk=ta[0])
        task.qty = Decimal(ta[1])
        task.save()
    for p in data['progress']:
        pr = ProgressReport.objects.get(pk=p[0])
        pr.complete = Decimal(p[1])
        pr.save()
