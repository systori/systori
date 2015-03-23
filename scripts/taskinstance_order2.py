import os
import re
import unicodedata
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
import django
django.setup()

from systori.apps.task.models import *

task = Task.objects.get(id=input("Task ID: "))

for ti in task.taskinstances.all():
    print("{} - {}".format(ti.id, ti.name))

new_order = input("New order: ").split(",")

for ti_id in new_order:
    ti = TaskInstance.objects.get(id=ti_id)
    print("{} - {}".format(ti.id, ti.name))

if input("Are you sure to save changes?: ") == "yes":
    for i, ti_id in enumerate(new_order):
        ti = TaskInstance.objects.get(id=ti_id)
        ti.order = i
        ti.save()
