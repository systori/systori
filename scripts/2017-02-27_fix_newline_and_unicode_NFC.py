import os
import unicodedata
import json
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
django.setup()

from systori.lib.accounting.tools import JSONEncoder
from systori.apps.company.models import Company
from systori.apps.project.models import Project
from systori.apps.task.models import Task, Group, Job, LineItem


def has_n(thing):
    return '\n' in thing

def normalize(thing):
    return unicodedata.normalize('NFC', thing)

def check_obj(thing):
    for attr in ['name', 'description']:
        value = getattr(thing, attr, '')
        setattr(thing, attr, normalize(value))
        value = getattr(thing, attr, '')
        setattr(thing, attr, value.replace('\n', '<br />'))
        value = getattr(thing, attr, '')
        setattr(thing, attr, value.strip())
    thing.save()


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

    for job in Job.objects.all():
        check_obj(job)
    for group in Group.objects.all():
        check_obj(group)
    for task in Task.objects.all():
        check_obj(task)
    for lineitem in LineItem.objects.all():
        check_obj(lineitem)
