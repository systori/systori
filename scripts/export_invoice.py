import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
import django
django.setup()

from django.core import serializers
from itertools import chain
from systori.apps.company.models import Company
from systori.apps.document.models import Invoice

if not len(sys.argv) == 3 or not sys.argv[2].isdigit():
    print('Usage: "python export_invoice.py mehr-handwerk 99"')
    sys.exit(1)

Company.objects.get(schema=sys.argv[1]).activate()

invoice = Invoice.objects.get(pk=sys.argv[2])
with open('invoice-'+sys.argv[1]+'-'+sys.argv[2]+'.xml', 'w') as f:
    serializers.serialize("xml", chain(
        [invoice.transaction],
        invoice.transaction.entries.all(),
        [invoice],
    ), stream=f)
