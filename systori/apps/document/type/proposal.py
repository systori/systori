from io import BytesIO
from reportlab.pdfgen import canvas
from django.utils.translation import ugettext_lazy as _


def serialize(project, form):

    proposal = {'version': '1.0'}

    if form.cleaned_data['add_terms']:
        proposal['terms'] = ['The Terms'] # TODO: Calculate the terms.


    proposal['jobs'] = []

    for job in project.billable_jobs:
        job_dict = {
            'code': job.code,
            'name': job.name,
            'taskgroups': []
        }
        proposal['jobs'].append(job_dict)

        for taskgroup in job.billable_taskgroups:
            taskgroup_dict = {
                'code': taskgroup.code,
                'name': taskgroup.name,
                'total': taskgroup.billable_total,
                'tasks': []
            }
            job_dict['taskgroups'].append(taskgroup_dict)

            for task in taskgroup.billable_tasks:
                task_dict = {
                    'code': task.instance.code,
                    'name': task.instance.full_name,
                    'complete': task.complete,
                    'unit': task.unit,
                    'price': task.instance.unit_price,
                    'total': task.fixed_price_billable,
                    'lineitems': []
                }
                taskgroup_dict['tasks'].append(task_dict)

                for lineitem in task.instance.lineitems.all():
                    lineitem_dict = {
                        'name': lineitem.name,
                        'qty': lineitem.unit_qty,
                        'unit': lineitem.unit,
                        'price': lineitem.price,
                        'price_per': lineitem.price_per_task_unit,
                    }
                    task_dict['lineitems'].append(lineitem_dict)


    proposal['transactions'] = []

    for record_type, date, record in get_transactions_table(self.project):

        txn = {
            'type': record_type,
            'amount': record.amount,
            'amount_base': record.amount_base,
            'amount_tax': record.amount_tax
        }

        if record_type == 'payment':
            txn['received'] = record.received_on

        proposal['transactions'].append(txn)


    return proposal


def render(proposal):

    with BytesIO() as buffer:
        p = canvas.Canvas(buffer)

        p.drawString(100, 100, "Hello world.")

        p.showPage()
        p.save()
        return buffer.getvalue()
