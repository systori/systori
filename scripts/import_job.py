import os, sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
import django

django.setup()

from django.core import serializers
from systori.apps.company.models import Company
from systori.apps.task.models import Job

if not len(sys.argv) == 3:
    print('Usage: "python import_job.py mehr-handwerk job-mehr-handwerk-99.xml"')
    sys.exit(1)

Company.objects.get(schema=sys.argv[1]).activate()

with open(sys.argv[2], "rb") as f:
    objs = serializers.deserialize("xml", f)
    next(objs).save()  # account
    root = next(objs)  # object for parent class of Job
    root.object.job = None
    root.save()
    for o in objs:
        o.save()
    print("Imported.")
