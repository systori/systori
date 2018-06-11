import os, sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
import django

django.setup()

from django.core import serializers
from systori.apps.company.models import Company

if not len(sys.argv) == 3:
    print(
        'Usage: "python import_invoice.py mehr-handwerk invoice-mehr-handwerk-99.xml"'
    )
    sys.exit(1)

Company.objects.get(schema=sys.argv[1]).activate()

with open(sys.argv[2], "r") as f:
    objects = serializers.deserialize("xml", f)
    for o in objects:
        o.save()
    print("Imported.")
