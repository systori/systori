import os
import re
import unicodedata
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
import django
django.setup()

from systori.apps.task.models import *

task_id = input("Please enter TASK ID: ")
task = Task.objects.get(id=task_id)

for ti in task.taskinstances.all():
    print("instance_order: {} instance_name: {}".format(ti.order, ti.name))

new_order = input("Please enter new Order comma-separated: ")
new_order = new_order.split(",")

for key, taskinstance in enumerate(task.taskinstances.all()):
    print("old id: {} new id: {}".format(taskinstance.order, new_order[key]))

if input("Are you sure to save changes?: ") == "yes":
    for key, taskinstance in enumerate(task.taskinstances.all()):
        taskinstance.order =  new_order[key]
        taskinstance.save()

