from io import BytesIO
from datetime import date
from decimal import Decimal

from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Spacer

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.apps.accounting.constants import TAX_RATE
from systori.apps.document.forms import InvoiceForm
from systori.lib.templatetags.customformatting import money, ubrdecimal

from .style import SystoriDocument, stylesheet, TableFormatter, ContinuationTable
from .style import PortraitStationaryCanvasWithoutFirstPage
from .invoice import collate_tasks, collate_tasks_total, serialize

from . import font

DEBUG_DOCUMENT = False  # Shows boxes in rendered output

def collate_payments(invoice, available_width):

    t = TableFormatter([0, 1, 1, 1], available_width, debug=DEBUG_DOCUMENT)
    t.style.append(('LEFTPADDING', (0, 0), (0, -1), 0))
    t.style.append(('RIGHTPADDING', (-1, 0), (-1, -1), 0))
    t.style.append(('BOTTOMPADDING', (0, 1), (-1, -1), 3*mm))
    t.style.append(('ALIGNMENT', (0, 0), (0, -1), "LEFT"))
    t.style.append(('ALIGNMENT', (1, 0), (-1, -1), "RIGHT"))
    t.style.append(('VALIGN', (0, 0), (-1, -1), "TOP"))

    t.style.append(('LINEBELOW', (0, 0), (-1, 0), 0.25, colors.black))
    t.style.append(('LINEAFTER', (0, 0), (-2, -1), 0.25, colors.black))

    t.row('', _("gross pay"), _("consideration"), _("VAT"))
    t.row_style('FONTNAME', 0, -1, font.bold)

    if len(invoice['transactions']) > 0:
        t.row(_("Job Performance"), money(invoice['total_gross']), money(invoice['total_base']), money(invoice['total_tax']))

    billable_amount = invoice['total_gross']

    for payment in invoice['transactions']:
        row = ['', money(payment['amount']), money(payment['amount_base']), money(payment['amount_tax'])]
        if payment['type'] == 'payment':
            received_on = date_format(payment['received_on'], use_l10n=True)
            row[0] = _('Your Payment on')+' '+received_on
        elif payment['type'] == 'discount':
            row[0] = _('Discount Applied')
        billable_amount += payment['amount']
        t.row(*row)

    t.row(_("Billable Total"), money(billable_amount), money(billable_amount/(TAX_RATE+Decimal('1'))), money(billable_amount/(TAX_RATE+Decimal('1'))*TAX_RATE))

    t.row_style('FONTNAME', 0, -1, font.bold)

    return t.get_table(ContinuationTable, repeatRows=1)

# def serialize(project):
#
#     jobs_dict_list = []
#
#     for job in project.billable_jobs:
#         job_dict = {
#             'code': job.code,
#             'name': job.name,
#             'taskgroups': []
#         }
#
#         for taskgroup in job.billable_taskgroups:
#             taskgroup_dict = {
#                 'code': taskgroup.code,
#                 'name': taskgroup.name,
#                 'description': taskgroup.description,
#                 'total': taskgroup.billable_total,
#                 'tasks': []
#             }
#             job_dict['taskgroups'].append(taskgroup_dict)
#
#             for task in taskgroup.billable_tasks:
#                 task_dict = {
#                     'code': task.instance.code,
#                     'name': task.instance.full_name,
#                     'description': task.instance.full_description,
#                     'complete': task.complete,
#                     'unit': task.unit,
#                     'price': task.instance.unit_price,
#                     'total': task.fixed_price_billable,
#                     'lineitems': []
#                 }
#                 taskgroup_dict['tasks'].append(task_dict)
#
#                 for lineitem in task.instance.lineitems.all():
#                     lineitem_dict = {
#                         'name': lineitem.name,
#                         'qty': lineitem.unit_qty,
#                         'unit': lineitem.unit,
#                         'price': lineitem.price,
#                         'price_per': lineitem.price_per_task_unit,
#                     }
#                     task_dict['lineitems'].append(lineitem_dict)
#         jobs_dict_list.append(job_dict)
#
#     transactions = []
#
#     for record_type, _, record in get_transactions_table(project):
#
#         if record_type in ('payment', 'discount'):
#
#             txn = {
#                 'type': record_type,
#                 'amount': record.amount,
#                 'amount_base': record.amount_base,
#                 'amount_tax': record.amount_tax
#             }
#
#             if record_type == 'payment':
#                 txn['received_on'] = record.received_on
#
#             transactions.append(txn)
#
#    return (jobs_dict_list, transactions)

def render(project, format):

    with BytesIO() as buffer:

        today = date_format(date.today(), use_l10n=True)

        itemized_listing = serialize(project, {})

        doc = SystoriDocument(buffer, topMargin=39*mm, debug=DEBUG_DOCUMENT)

        flowables = [

            Paragraph(_("Itemized listing {}").format(date.today), stylesheet['h2']),

            Paragraph(_("Project") + ": {}".format(project.name), stylesheet['Normal']),
            Paragraph(_("Date") + ": {}".format(today), stylesheet['Normal']),

            Spacer(0, 10*mm),

            collate_payments(itemized_listing, doc.width),

            Spacer(0, 10*mm),

            collate_tasks(itemized_listing, doc.width),

            Spacer(0, 4*mm),

            collate_tasks_total(itemized_listing, doc.width),
            ]

        if format == 'print':
            doc.build(flowables)
        else:
            doc.build(flowables, canvasmaker=PortraitStationaryCanvasWithoutFirstPage)


        return buffer.getvalue()
