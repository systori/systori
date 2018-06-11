import os
import re
import unicodedata

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
import django

django.setup()

from systori.apps.user.models import User
from systori.apps.company.models import *

company = Company.objects.get(schema="mehr_handwerk")
company.activate()


from systori.apps.project.models import Project

for project in Project.objects.all():
    for proposal in project.proposals.all():
        if len(proposal.json) == 0:
            proposal.delete()
            # print("found some propsals")
    for invoice in project.invoices.all():
        if len(invoice.json) == 0:
            # print("projekt: {}".format(project.id))
            invoice.delete()
            # print("found some invoices")
