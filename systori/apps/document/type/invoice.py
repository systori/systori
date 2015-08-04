from io import BytesIO
from datetime import date

from reportlab.lib.units import mm
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, KeepTogether, PageBreak
from reportlab.lib import colors

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.lib.templatetags.customformatting import ubrdecimal, money
from systori.apps.accounting.utils import get_transactions_table

from .style import SystoriDocument, TableFormatter, ContinuationTable, stylesheet, force_break, p, b, nr
from .style import PortraitStationaryCanvas
from . import font


DEBUG_DOCUMENT = False  # Shows boxes in rendered output


def collate_tasks(invoice, available_width):

    t = TableFormatter([1, 0, 1, 1, 1, 1], available_width, debug=DEBUG_DOCUMENT)
    t.style.append(('LEFTPADDING', (0, 0), (-1, -1), 0))
    t.style.append(('RIGHTPADDING', (-1, 0), (-1, -1), 0))
    t.style.append(('VALIGN', (0, 0), (-1, -1), 'TOP'))
    t.style.append(('LINEABOVE', (0, 'splitfirst'), (-1, 'splitfirst'), 0.25, colors.black))

    t.row(_("Pos."), _("Description"), _("Amount"), '', _("Price"), _("Total"))
    t.row_style('FONTNAME', 0, -1, font.bold)
    t.row_style('ALIGNMENT', 2, 3, "CENTER")
    t.row_style('ALIGNMENT', 4, -1, "RIGHT")
    t.row_style('SPAN', 2, 3)

    for job in invoice['jobs']:
        t.row(b(job['code']), b(job['name']))
        t.row_style('SPAN', 1, -1)

        for taskgroup in job['taskgroups']:
            t.row(b(taskgroup['code']), b(taskgroup['name']))
            t.row_style('SPAN', 1, -1)

            for task in taskgroup['tasks']:
                t.row(p(task['code']), p(task['name']))
                t.row_style('SPAN', 1, -2)

                t.row('', '', ubrdecimal(task['complete']), p(task['unit']), money(task['price']), money(task['total']))
                t.row_style('ALIGNMENT', 1, -1, "RIGHT")

                t.row_style('BOTTOMPADDING', 0, -1, 10)

                t.keep_previous_n_rows_together(2)

            t.row('', b('{} {} - {}'.format(_('Total'), taskgroup['code'], taskgroup['name'])),
                  '', '', '', money(taskgroup['total']))
            t.row_style('FONTNAME', 0, -1, font.bold)
            t.row_style('ALIGNMENT', -1, -1, "RIGHT")
            t.row_style('SPAN', 1, 4)

            t.row('')

    return t.get_table(ContinuationTable, repeatRows=1)


def collate_tasks_total(invoice, available_width):

    t = TableFormatter([0, 1], available_width, debug=DEBUG_DOCUMENT)
    t.style.append(('RIGHTPADDING', (-1, 0), (-1, -1), 0))
    t.style.append(('LEFTPADDING', (0, 0), (0, -1), 0))
    t.style.append(('FONTNAME', (0, 0), (-1, -1), font.bold))
    t.style.append(('ALIGNMENT', (0, 0), (-1, -1), "RIGHT"))

    for job in invoice['jobs']:
        for taskgroup in job['taskgroups']:
            t.row(b('{} {} - {}'.format(_('Total'), taskgroup['code'], taskgroup['name'])),
                  money(taskgroup['total']))
    t.row_style('LINEBELOW', 0, 1, 0.25, colors.black)

    t.row(_("Total without VAT"), money(invoice['total_base']))
    t.row("19,00% "+_("VAT"), money(invoice['total_tax']))
    t.row(_("Total including VAT"), money(invoice['total_gross']))

    return t.get_table()


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

    t.row(_("Invoice Total"), money(invoice['total_gross']), money(invoice['total_base']), money(invoice['total_tax']))

    for payment in invoice['transactions']:
        row = ['', money(payment['amount']), money(payment['amount_base']), money(payment['amount_tax'])]
        if payment['type'] == 'payment':
            received_on = date_format(date(*map(int, payment['received_on'].split('-'))), use_l10n=True)
            row[0] = _('Your Payment on')+' '+received_on
        elif payment['type'] == 'discount':
            row[0] = _('Discount Applied')
        t.row(*row)

    t.row(_("Remaining amount"), money(invoice['balance_gross']), money(invoice['balance_base']), money(invoice['balance_tax']))
    t.row_style('FONTNAME', 0, -1, font.bold)

    return t.get_table(ContinuationTable, repeatRows=1)


def render(invoice, format):

    with BytesIO() as buffer:

        invoice_date = date_format(date(*map(int, invoice['date'].split('-'))), use_l10n=True)

        doc = SystoriDocument(buffer, debug=DEBUG_DOCUMENT)
        flowables = [

            Paragraph(force_break("""\
            {business}
            z.H. {salutation} {first_name} {last_name}
            {address}
            {postal_code} {city}
            """.format(**invoice)), stylesheet['Normal']),

            Spacer(0, 18*mm),

            Paragraph(invoice.get('title') or _("Invoice"), stylesheet['h2']),

            Spacer(0, 4*mm),

            Paragraph(invoice_date, stylesheet['NormalRight']),
            Paragraph(_("Invoice No.")+" "+invoice['invoice_no'], stylesheet['NormalRight']),
            Paragraph(_("Please indicate the correct invoice number on your payment."),
                      ParagraphStyle('', parent=stylesheet['Small'], alignment=TA_RIGHT)),

            Paragraph(force_break(invoice['header']), stylesheet['Normal']),

            Spacer(0, 4*mm),

            collate_payments(invoice, doc.width),

            Spacer(0, 4*mm),

            KeepTogether(Paragraph(force_break(invoice['footer']), stylesheet['Normal'])),

            PageBreak(),

            Paragraph(_("Measurement Listing of Invoice No. %(invoice_no)s from %(invoice_date)s")
                        % {'invoice_no':invoice['invoice_no'], 'invoice_date':invoice_date}, stylesheet['h4']),

            Spacer(0, 2*mm),

            collate_tasks(invoice, doc.width),

            Spacer(0, 4*mm),

            collate_tasks_total(invoice, doc.width),

            ]

        if format == 'print':
            doc.build(flowables)
        else:
            doc.build(flowables, canvasmaker=PortraitStationaryCanvas)


        return buffer.getvalue()


def serialize(project, form):

    contact = project.billable_contact.contact

    invoice = {

        'version': '1.0',

        'title': form.cleaned_data['title'],
        'date': form.cleaned_data['document_date'],
        'invoice_no': form.cleaned_data['invoice_no'],

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
        invoice['add_terms'] = True  # TODO: Calculate the terms.

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
                'description': taskgroup.description,
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

    for record_type, _, record in get_transactions_table(project):

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
