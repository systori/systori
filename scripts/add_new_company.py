import os
import getpass

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
import django

django.setup()

from systori.apps.company.models import Company, Worker

schema = input("schema name: ")
name = input("company name: ")
print(schema)
company = Company.objects.create(schema=schema, name=name, is_active=True)

company.activate()

from systori.apps.user.models import User

first_name = input("first name: ")
last_name = input("last name: ")
email = input("email: ")
password = getpass.getpass()

user = User.objects.create(first_name=first_name, last_name=last_name, email=email)
user.set_password(password)
user.save()

for email in ["lex@damoti.com", "mr@mehr-handwerk.de"]:
    Worker.objects.create(company=company, user=User.objects.get(email=email))

worker = Worker.objects.create(company=company, user=user, is_owner=True)

from systori.apps.project.models import Project

Project.objects.create(name="Template Project", is_template=True)

from systori.apps.accounting.workflow import create_chart_of_accounts

create_chart_of_accounts()
