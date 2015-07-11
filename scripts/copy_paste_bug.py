import os
import re
import unicodedata

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
import django

django.setup()

from systori.apps.task.models import *
from systori.apps.project.models import *

p22 = Project.objects.get(id=22)

for job in p22.jobs.all():
    for taskgroup in job.taskgroups.all():
        print("before name: {}".format(taskgroup.name))
        print("before description: {}".format(taskgroup.description))
        name_striped = taskgroup.name.strip()
        description_striped = taskgroup.description.strip()
        taskgroup.name = re.sub('\s+', ' ', name_striped)
        taskgroup.name = unicodedata.normalize('NFC', taskgroup.name)
        taskgroup.description = re.sub('\s+', ' ', description_striped)
        taskgroup.description = unicodedata.normalize('NFC', taskgroup.description)
        print("after name: {}".format(taskgroup.name))
        print("after description: {}".format(taskgroup.description))
        taskgroup.save()
        for task in taskgroup.tasks.all():
            print("before name: {}".format(task.name))
            print("before description: {}".format(task.description))
            name_striped = task.name.strip()
            description_striped = task.description.strip()
            task.name = re.sub('\s+', ' ', name_striped)
            task.name = unicodedata.normalize('NFC', task.name)
            task.description = re.sub('\s+', ' ', description_striped)
            task.description = unicodedata.normalize('NFC', task.description)
            print("after name: {}".format(task.name))
            print("after description: {}".format(task.description))
            print("\n\n\n")
            task.save()
