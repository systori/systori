import os
import re
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ubrblik.settings")
import django
django.setup()

from ubrblik.apps.task.models import *
from ubrblik.apps.project.models import *

p22 = Project.objects.get(id=22)

for job in p22.jobs.all():
    for taskgroup in job.taskgroups.all():
        print("before name: {}".format(taskgroup.name))
        print("before description: {}".format(taskgroup.description))
        name_striped = taskgroup.name.strip()
        description_striped = taskgroup.description.strip()
        taskgroup.name = re.sub('\s+',' ',name_striped)
        taskgroup.description = re.sub('\s+',' ',description_striped)
        print("after name: {}".format(taskgroup.name))
        print("after description: {}".format(taskgroup.description))
        for c in taskgroup.name:
            if(ord(c)==776):
                task.name = task.name.replace(c,"")
        taskgroup.save()
        for task in taskgroup.tasks.all():
            print("before name: {}".format(task.name))
            print("before description: {}".format(task.description))
            name_striped = task.name.strip()
            description_striped = task.description.strip()
            task.name = re.sub('\s+',' ',name_striped)
            task.description = re.sub('\s+',' ',description_striped)
            print("after name: {}".format(task.name))
            print("after description: {}".format(task.description))
            for c in task.name:
                if(ord(c)==776):
                    print("{}->{}".format(c, ord(c)))
                    task.name = task.name.replace(c,"")
            for c in task.description:
                if(ord(c)==776):
                    print("{}->{}".format(c, ord(c)))
                    task.description = task.description.replace(c,"")
            print("\n\n\n")
            task.save()

