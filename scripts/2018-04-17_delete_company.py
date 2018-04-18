import os
import getpass

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
import django
from django.db import connection
from django.db.utils import ProgrammingError
django.setup()

from systori.apps.company.models import Company, Worker
from systori.apps.user.models import User
from systori.apps.project.models import Project
from systori.apps.main.models import Note


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


if __name__ == '__main__':
    while True:
        print("Today is April 2018. this script is probably outdated!")
        print("available company schematas: {}".format( [c.schema for c in Company.objects.all()] ))
        try:
            schema = input("schema name: ")
            company = Company.objects.get(schema=schema)
        except:
            print("can't find anything with that schema.\n\n\n")
            continue
        try:
            company.activate()
        except ProgrammingError:
            break
        try:
            print('Company {} with schema {}\n'.format(company.name, company.schema))
            print('has {} projects\n'.format(Project.objects.count()))
            print('has {} workers\n'.format(Worker.objects.filter(company=company).count()))
        except:
            pass #  already deleted company

        for worker in Worker.objects.filter(company=company).all():
            print('worker {} with related user {}'.format(worker, worker.user))
            if worker.user.companies.count() == 1:
                print('--> user {} is only associated with {}'.format(worker.user, company))


        if input("do you want to delete the company?:") == "yes":
            if input("give me the schema again:") == schema:

                try:
                    Note.objects.all().delete()
                except ProgrammingError:
                    pass #  already deleted

                existing_workers = [worker.id for worker in Worker.objects.all()]
                for worker in Worker.objects.filter(company=company).all():
                    if worker.user.companies.count() == 1:
                        worker.user.delete()
                    worker_id = worker.id
                    worker.delete()
                try:
                    for project in Project.objects.all():
                        project.delete()
                except:
                    pass #  already deleted
                with connection.cursor() as cursor:
                    cursor.execute("select * from public.company_contract")
                    company_contracts = dictfetchall(cursor)
                    for contract in company_contracts:
                        if contract['worker_id'] in existing_workers: #  worker still exists
                            continue
                        elif contract['worker_id'] is None:
                            print("company_contract with ID {} has no worker assigned.".format(contract['id']))
                            continue
                        else:
                            cursor.execute("DELETE FROM public.company_contract WHERE worker_id = '{}'".format(contract['worker_id']))
                    cursor.execute("delete from public.company_worker where company_id = '{}'".format(schema))
                    cursor.execute("DELETE FROM public.company_company WHERE company_company.schema = '{}'".format(schema))
                    try:
                        cursor.execute('DROP SCHEMA "{}" CASCADE'.format(schema))
                    except ProgrammingError:
                        pass #  already deleted
        print("#### done ####\n\n")
