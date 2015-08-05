import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
import django
django.setup()

from p83_parser import parse_p83_file
from systori.apps.project.models import *
from systori.apps.company.models import *

project = parse_p83_file('gaeb2000_file.p83')

Company.objects.get(schema='mehr_handwerk').activate()

print("Project:")
for key, value in project['attrs'].items():
    print(" {}: {}".format(key, value))
print()

for job in project['jobs']:
    print("Job:")
    for key, value in job['attrs'].items():
        print(" {}: {}".format(key, value))
    print()

    for taskgroup in job['taskgroups']:
        print("    Task Group:")
        for key, value in taskgroup['attrs'].items():
            print("     {}: {}".format(key, value))
        print()

        for task in taskgroup['tasks']:
            print("      Task:")
            for key, value in task['attrs'].items():
                print("       {}: {}".format(key, value))
            print()
