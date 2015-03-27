import os
import re
import unicodedata
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
import django
django.setup()

from systori.apps.task.models import *
from systori.apps.project.models import *

p = Project.objects.get(id=input("Project ID: "))

for job in p.jobs.all():
    for taskgroup in job.taskgroups.all():
        for task in taskgroup.tasks.all():
            if task.taskinstances.all():
                for taskinstance in task.taskinstances.all():
                    print("found taskinstances: {}".format(taskinstance))
            else:
                print("missing taskinstance at {}:{}\n".format(task.id, task.name))
                if input("Add missing taskinstance: ") == "yes":
                    TaskInstance.objects.create(task=task, selected=True)
