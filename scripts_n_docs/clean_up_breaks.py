import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
import django

django.setup()

import json
from django.core.urlresolvers import reverse
from systori.apps.company.models import Company
from systori.apps.project.models import Project


def has_br(thing):
    return '<br>' in thing


def check_obj(obj):
    fixed = False
    for attr in ['name', 'description']:
        value = getattr(obj, attr, '')
        if has_br(value):
            setattr(obj, attr, value.replace('<br>', '<br />'))
            fixed = True
    if fixed:
        obj.save()
        return 1
    return 0


for company in Company.objects.all():
    company.activate()
    print(company.name)

    for project in Project.objects.all():

        for proposal in project.proposals.all():
            json_str = json.dumps(proposal.json)
            if has_br(json_str):
                print('https://systori.com'+reverse('proposal.pdf', args=[proposal.project.id, 'email', proposal.id]))
                proposal.json = json.loads(json_str.replace('<br>', '<br />'))
                proposal.save()

        for invoice in project.invoices.all():
            json_str = json.dumps(invoice.json)
            if has_br(json_str):
                print('https://systori.com'+reverse('invoice.pdf', args=[invoice.project.id, 'email', invoice.id]))
                invoice.json = json.loads(json_str.replace('<br>', '<br />'))
                invoice.save()

        for job in project.jobs.all():
            fixed = 0
            for taskgroup in job.taskgroups.all():
                fixed += check_obj(taskgroup)
                for task in taskgroup.tasks.all():
                    fixed += check_obj(task)
                    for instance in task.taskinstances.all():
                        fixed += check_obj(instance)
                        for lineitem in instance.lineitems.all():
                            fixed += check_obj(lineitem)
            if fixed > 0:
                print('https://systori.com'+reverse('tasks', args=[job.project.id, job.id]))
