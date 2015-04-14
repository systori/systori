import os, decimal
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
import django
django.setup()

from systori.apps.accounting.skr03 import *
from systori.apps.project.models import *

p = Project.objects.get(id=18)
partial_credit(p, decimal.Decimal(5063.62), was_discount_applied=False)
