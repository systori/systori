import os
import getpass

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
import django
from django.db import connection
django.setup()

from systori.apps.company.models import Company, Worker
from systori.apps.user.models import User
from systori.apps.project.models import Project


if __name__ == '__main__':
    while True:
        companies = [c.schema for c in Company.objects.all()]
        print("available company schematas: {}".format(companies))
        schema = input("schema name: ")
        company = Company.objects.get(schema=schema)
        company.activate()
        print('Company {} with schema {}\n'.format(company.name, company.schema))
        print('has {} projects\n'.format(Project.objects.count()))
        print('has {} workers\n'.format(Worker.objects.filter(company=company).count()))
        for worker in Worker.objects.filter(company=company).all():
            print('worker {} with related user {}'.format(worker, worker.user))
            if worker.user.companies.count() == 1:
                print('--> user {} is only associated with {}'.format(worker.user, company))

        if input("do you want to delete the company?:") == "yes":
            if input("give me the schema again:") == schema:
                for worker in Worker.objects.filter(company=company).all():
                    if worker.user.companies.count() == 1:
                        worker.user.delete()
                    worker.delete()
                for project in Project.objects.all():
                    project.delete()
                with connection.cursor() as cursor:
                    cursor.execute('DROP SCHEMA {} CASCADE'.format(schema))
        print("#### done ####\n\n")
