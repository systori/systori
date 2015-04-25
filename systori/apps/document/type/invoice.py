from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from systori.apps.accounting.utils import get_transactions_table
from django.utils.translation import ugettext as _


def txt(t):
    return Paragraph(str(t), ParagraphStyle('',fontName='Helvetica',fontSize=12,leading=17))

def render(invoice):

    with BytesIO() as buffer:
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        lines = []
        for job in invoice['jobs']:
            lines.append([txt(job['code']), txt(job['name'])])

            for taskgroup in job['taskgroups']:
                lines.append([txt(taskgroup['code']), txt(taskgroup['name'])])

                for task in taskgroup['tasks']:
                    lines.append([txt(task['code']), txt(task['name'])])
                    lines.append(['', '', txt(task['complete']), txt(task['unit']), txt(task['price']), txt(task['total'])])
                
                lines.append(['', txt('Total {} - {}'.format(taskgroup['code'], taskgroup['name'])), txt(taskgroup['total'])])

        for job in invoice['jobs']:
            for taskgroup in job['taskgroups']:
                lines.append(['', txt('Total {} - {}'.format(taskgroup['code'], taskgroup['name'])), txt(taskgroup['total'])])

        payments = [['', txt(invoice['total_gross']), txt(invoice['total_base']), txt(invoice['total_tax'])]]
        for payment in invoice['transactions']:
            row = ['', txt(payment['amount']), txt(payment['amount_base']), txt(payment['amount_tax'])]
            if payment['type'] == 'payment':
                row[0] = txt(_('Your Payment on') + ' {}'.format(payment['received_on']))
            elif payment['type'] == 'discount':
                row[0] = txt(_('Discount Applied'))
            payments.append(row)
        payments.append(['', txt(invoice['balance_gross']), txt(invoice['balance_base']), txt(invoice['balance_tax'])])

        doc.build([

            txt(invoice['business']),
            txt("z.H. {salutation} {first_name} {last_name}".format(**invoice)),
            txt(invoice['address']),
            txt("{postal_code} {city}".format(**invoice)),

            txt(invoice['header']),

            Table(lines),

            Table(payments),

            txt(invoice['footer']),

        ])
        return buffer.getvalue()




def serialize(project, form):

    contact = project.billable_contact.contact

    invoice = {

        'version': '1.0',

        'date': form.cleaned_data['document_date'],

        'header': form.cleaned_data['header'],
        'footer': form.cleaned_data['footer'],
        
        'business': contact.business,
        'salutation': contact.salutation,
        'first_name': contact.first_name,
        'last_name': contact.last_name,
        'address': contact.address,
        'postal_code': contact.postal_code,
        'city': contact.city,
        
        'total_gross': project.billable_gross_total,
        'total_base': project.billable_total,
        'total_tax': project.billable_tax_total,

        'balance_gross': project.account.balance,
        'balance_base': project.account.balance_base,
        'balance_tax': project.account.balance_tax,

    }

    if form.cleaned_data['add_terms']:
        invoice['add_terms'] = True # TODO: Calculate the terms.

    invoice['jobs'] = []

    for job in project.billable_jobs:
        job_dict = {
            'code': job.code,
            'name': job.name,
            'taskgroups': []
        }
        invoice['jobs'].append(job_dict)

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
                    'description': task.instance.full_description,
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


    invoice['transactions'] = []

    for record_type, date, record in get_transactions_table(project):

        if record_type in ('payment', 'discount'):

            txn = {
                'type': record_type,
                'amount': record.amount,
                'amount_base': record.amount_base,
                'amount_tax': record.amount_tax
            }

            if record_type == 'payment':
                txn['received_on'] = record.received_on

            invoice['transactions'].append(txn)


    return invoice
