"""
This script lists the TaskInstance(s) of a given Task-ID
it prints the "order" Integer of the Instances starting from 0
f.e.
0 - A
1 - B
2 - C
it expects as the input the "new order" with given Integer values.
f.e.
2,0,1
result:
0 - B
1 - C
2 - A
"""

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
        taskinstance.order = new_order[key]
        taskinstance.save()
