import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
import django
django.setup()

from django.core import serializers
from itertools import chain
from systori.apps.company.models import Company
from systori.apps.task.models import Job

if not len(sys.argv) == 3 or not sys.argv[2].isdigit():
    print('Usage: "python export_job.py mehr-handwerk 99"')
    sys.exit(1)

Company.objects.get(schema=sys.argv[1]).activate()

job = Job.objects.get(pk=sys.argv[2])
with open('job-'+sys.argv[1]+'-'+sys.argv[2]+'.xml', 'w') as f:
    serializers.serialize("xml", chain(
        [job.account, job.root, job],
        job.all_groups.all(),
        job.all_tasks.all(),
        job.all_lineitems.all(),
    ), stream=f)
