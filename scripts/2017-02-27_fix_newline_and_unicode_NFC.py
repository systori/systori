import os
import unicodedata
import json
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
django.setup()

from systori.lib.accounting.tools import JSONEncoder
from systori.apps.company.models import Company
from systori.apps.project.models import Project
from systori.apps.task.models import Task, Group


def has_n(thing):
    return '\n' in thing

def normalize(thing):
    return unicodedata.normalize('NFC', thing)

def check_obj(thing):
    fixed = 0
    for attr in ['name', 'description']:
        value = getattr(thing, attr, '')
        if value != normalize(value):
            setattr(thing, attr, normalize(value))
            fixed = 1
        value = getattr(thing, attr, '')
        if has_n(value):
            setattr(thing, attr, value.replace('\n', '<br />'))
            fixed = 1
        setattr(thing, attr, value.strip())
    if fixed:
        thing.save()
        return 1
    return 0

for company in Company.objects.all():
    company.activate()
    print(company.name)

    for project in Project.objects.all():

        for proposal in project.proposals.all():
            json_str = json.dumps(proposal.json, cls=JSONEncoder, ensure_ascii=False)
            proposal.json = json.loads(normalize(json_str))
            proposal.save()

        for invoice in project.invoices.all():
            json_str = json.dumps(invoice.json, cls=JSONEncoder, ensure_ascii=False)
            invoice.json = json.loads(normalize(json_str))
            invoice.save()

        for job in project.jobs.all():
            check_obj(job)
            for group in Group.objects.filter(job=job):
                check_obj(group)
            for task in Task.objects.filter(job=job):
                check_obj(task)
                for lineitem in task.lineitems.all():
                    check_obj(lineitem)
