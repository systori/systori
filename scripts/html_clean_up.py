import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
import django

django.setup()

import re
from systori.apps.project.models import *
from systori.apps.company.models import *


DEBUG = False


br = re.compile("(?!<br>)<(p|br|div)[^>]*>", re.IGNORECASE)
tag = re.compile("<(?!br).*?>")
space = re.compile("\s+")


def clean(obj, field, remove_breaks=False):

    value = getattr(obj, field)

    if remove_breaks:
        # remove all <br>/<p>/<div> tags
        value, changed1 = br.subn(" ", value)

    else:
        # normalize all <br>/<p>/<div> tags to <br>
        value, changed1 = br.subn("<br>", value)

    # remove anything that's not a <br>
    value, changed2 = tag.subn(" ", value)

    if changed1 + changed2 > 0:
        # if we removed HTML we probably need to clean spacing too
        value = space.sub(" ", value)
        if DEBUG:
            print("=" * 50)
            print(getattr(obj, field))
            print("-" * 50) if remove_breaks else print("+" * 50)
            print(value)
        setattr(obj, field, value)
        return True

    return False


FIELDS = [
    #    field,         single line
    ("name", True),
    ("description", False),
]


def clean_n_save(obj):

    save = False
    for field, remove_br in FIELDS:
        if hasattr(obj, field) and clean(obj, field, remove_br):
            save = True

    if save:
        print("saving...")
        obj.save()
        return 1

    return 0


Company.objects.get(schema="mehr_handwerk").activate()

for project in Project.objects.all():
    for job in project.jobs.all():
        j = 0
        for taskgroup in job.taskgroups.all():
            j += clean_n_save(taskgroup)
            for task in taskgroup.tasks.all():
                j += clean_n_save(task)
                for instance in task.taskinstances.all():
                    j += clean_n_save(instance)
                    for lineitem in instance.lineitems.all():
                        j += clean_n_save(lineitem)
        if j > 0:
            print("Project: %s, Job: %s" % (project.name, job.name))
