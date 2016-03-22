import os; os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
import django; django.setup()
from glob import glob
from decimal import Decimal as D
from django.db import transaction
from systori.apps.project.models import Project
from systori.apps.accounting.models import create_account_for_job
from systori.apps.company.models import Company
from systori.apps.task.models import Job, TaskGroup, Task, TaskInstance, LineItem


TEST_RUN = False  # whether to reset database after running


def clean(s):
    return s[2:-7].strip()


def parse(file_path):

    data = {}

    with open(file_path, encoding='cp437') as f:

        task_group_code = None

        for line in f.readlines():

            if line.startswith('11'):
                task_group_code, _ = clean(line).split()

            if line.startswith('12'):
                task_group_name = clean(line)
                assert task_group_code is not None
                assert task_group_code not in data
                data[task_group_code] = {
                    'name': task_group_name,
                    'tasks': []
                }

            if line.startswith('21'):
                assert None not in (task_group_code, task_group_name)
                try:
                    task_code, _, qty_unit = clean(line).split()
                except ValueError:
                    task_code = '9'*10  # sort blank code to end
                    _, qty_unit = clean(line).split()
                task_qty = D(qty_unit[:11])/D(1000)
                task_unit = {
                    'ST': 'Stk',
                    'M': 'm',
                    'M2': 'm²',
                    'M3': 'm³',
                    'PSH': 'Psch'
                }[qty_unit[11:]]
                data[task_group_code]['tasks'].append(
                    [task_code, '', task_qty, task_unit, '']
                )

            if line.startswith('25'):
                assert data[task_group_code]['tasks'][-1][1] == ''
                data[task_group_code]['tasks'][-1][1] = clean(line)

            if line.startswith('26'):
                data[task_group_code]['tasks'][-1][-1] += clean(line)+'<br />'

    return data


def main():

    Company.objects.get(schema='mehr_handwerk').activate()

    for file_path in glob('d83_files/*.d83'):

        data = parse(file_path)

        project = Project.objects.create(name=os.path.basename(file_path))
        job = Job.objects.create(job_code=1, name='Default', project=project)
        job.account = create_account_for_job(job)
        job.save()

        for group, details in data.items():
            taskgroup = TaskGroup.objects.create(name=group, job=job)
            tasks = details['tasks']
            tasks.sort()
            for t in tasks:
                task = Task.objects.create(taskgroup=taskgroup, name=t[1], qty=t[2], unit=t[3], description=t[4])
                LineItem.objects.create(
                    taskinstance=TaskInstance.objects.create(task=task, selected=True),
                    name='Kalkulation',
                    unit_qty=1, unit='Stk', price=D(0)
                )


if __name__ == "__main__":

    if TEST_RUN:
        # Start Transaction
        atom = transaction.atomic()
        atom.__enter__()

    main()

    if TEST_RUN:
        # Rollback Transaction
        transaction.set_rollback(True)
        atom.__exit__(None, None, None)
