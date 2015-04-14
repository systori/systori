import os, decimal
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
import django
django.setup()

from systori.apps.accounting.skr03 import *
from systori.apps.project.models import *

p6 = Project.objects.get(id=6)
partial_credit(p6, decimal.Decimal(200), was_discount_applied=True)
