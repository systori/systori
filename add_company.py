import os
import re
import unicodedata

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
import django

django.setup()

from systori.apps.user.models import User
from systori.apps.company.models import *

company = Company.objects.create(
    schema=input("Schema: "),
    name=input("Name: ")
)

for user in ['lex', 'mr']:
    Access.objects.create(
        company=company,
        user=User.objects.get(username=user)
    )

company.activate()

from systori.apps.project.models import Project

Project.objects.create(name="Template Project", is_template=True)

from systori.apps.accounting.workflow import create_chart_of_accounts

create_chart_of_accounts()
