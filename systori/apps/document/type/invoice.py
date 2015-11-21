"""
JSON Version Log
================
1.2
 - major refactoring, renamed fields, added new fields
 - coincided with project to job based account switch
1.1
 - Added is_flat_invoice attribute.
1.0
 - Initial Version.
"""

from io import BytesIO
from decimal import Decimal
from datetime import date

from reportlab.lib.units import mm
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, KeepTogether, PageBreak
from reportlab.lib import colors

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.lib.templatetags.customformatting import ubrdecimal, money
from systori.apps.accounting.utils import get_transactions_for_jobs
from systori.apps.accounting.constants import TAX_RATE

from .style import SystoriDocument, TableFormatter, ContinuationTable, stylesheet, force_break, p, b
from .style import LetterheadCanvas, NumberedCanvas
from .style import calculate_table_width_and_pagesize
from .style import heading_and_date, get_address_label, get_address_label_spacer
from . import font


DEBUG_DOCUMENT = False  # Shows boxes in rendered output


def collate_tasks(invoice, available_width):

    t = TableFormatter([1, 0, 1, 1, 1, 1], available_width, debug=DEBUG_DOCUMENT)
    t.style.append(('LEFTPADDING', (0, 0), (-1, -1), 0))
    t.style.append(('RIGHTPADDING', (-1, 0), (-1, -1), 0))
    t.style.append(('VALIGN', (0, 0), (-1, -1), 'TOP'))
    t.style.append(('LINEABOVE', (0, 'splitfirst'), (-1, 'splitfirst'), 0.25, colors.black))

    t.row(_("Pos."), _("Description"), _("Amount"), '', _("Price"), _("Total"))

    description_width = sum(t.get_widths()[1:6])

    for job in invoice['debits']:
        t.row(b(job['code']), b(job['name']))
        t.row_style('SPAN', 1, -1)

        for taskgroup in job['taskgroups']:
            t.row(b(taskgroup['code']), b(taskgroup['name']))
            t.row_style('SPAN', 1, -1)
            t.keep_next_n_rows_together(2)

            for task in taskgroup['tasks']:
                t.row(p(task['code']), p(task['name']))
                t.row_style('SPAN', 1, -2)

                t.row('', '', ubrdecimal(task['complete']), p(task['unit']), money(task['price']), money(task['total']))
                t.row_style('ALIGNMENT', 1, -1, "RIGHT")
                t.keep_previous_n_rows_together(2)

            t.row('', b('{} {} - {}'.format(_('Total'), taskgroup['code'], taskgroup['name'])),
                  '', '', '', money(taskgroup['total']))
            t.row_style('FONTNAME', 0, -1, font.bold)
            t.row_style('ALIGNMENT', -1, -1, "RIGHT")
            t.row_style('SPAN', 1, 4)
            t.row_style('VALIGN', 0, -1, "BOTTOM")

            t.row('')

    return t.get_table(ContinuationTable, repeatRows=1)


def collate_tasks_total(invoice, available_width):

    t = TableFormatter([0, 1], available_width, debug=DEBUG_DOCUMENT)
    t.style.append(('RIGHTPADDING', (-1, 0), (-1, -1), 0))
    t.style.append(('LEFTPADDING', (0, 0), (0, -1), 0))
    t.style.append(('FONTNAME', (0, 0), (-1, -1), font.bold))
    t.style.append(('ALIGNMENT', (0, 0), (-1, -1), "RIGHT"))

    for job in invoice['debits']:
        for taskgroup in job['taskgroups']:
            t.row(b('{} {} - {}'.format(_('Total'), taskgroup['code'], taskgroup['name'])),
                  money(taskgroup['total']))
    t.row_style('LINEBELOW', 0, 1, 0.25, colors.black)

    t.row(_("Total without VAT"), money(invoice['debited_net']))
    t.row("19,00% "+_("VAT"), money(invoice['debited_tax']))
    t.row(_("Total including VAT"), money(invoice['debited_gross']))

    return t.get_table()


def collate_history(invoice, available_width):

    t = TableFormatter([0, 1, 1, 1, 1], available_width, debug=DEBUG_DOCUMENT)
    t.style.append(('ALIGNMENT', (0, 0), (0, -1), "LEFT"))
    t.style.append(('ALIGNMENT', (1, 0), (-1, -1), "RIGHT"))
    t.style.append(('VALIGN', (0, 0), (-2, -1), "TOP"))
    t.style.append(('VALIGN', (-1, 0), (-1, -1), "BOTTOM"))
    t.style.append(('RIGHTPADDING', (-1, 0), (-1, -2), 0))

    t.style.append(('LINEBELOW', (0, 0), (-1, 0), 0.25, colors.black))
    t.style.append(('LINEABOVE', (0, -1), (-1, -1), 0.25, colors.black))
    t.style.append(('LINEAFTER', (0, 0), (-2, -2), 0.25, colors.black))

    t.row('', _("consideration"), _("tax"), _("gross"), _("balance"))
    t.row_style('FONTNAME', 0, -1, font.bold)

    last_txn_idx = len(invoice['transactions'])-1
    for txn_idx, txn in enumerate(invoice['transactions']):

        row = []
        rows_to_keep = 0

        description = {
            'payment': _('Payment'),
            'invoice': _('Partial Invoice'),
            'final-invoice': _('Final Invoice')
        }[txn['type']]

        if txn.get('invoice_id', None) == invoice['id']:
            description = _('This Invoice')

        row += [description]

        for col in ['net', 'tax']:
            row += [money(txn[col]) if txn[col] else '']

        if txn.get('discount_applied', 0):
            row += [money(txn['payment_applied'])]
        else:
            row += [money(txn['gross'])]

        t.row(*row)
        rows_to_keep += 1

        if txn.get('discount_applied', 0):
            t.row(_('Discount'), '', '', money(txn['discount_applied']))
            rows_to_keep += 1

        row = [date_format(date(*map(int, txn['date'].split('-'))), use_l10n=True), '', '', '', '']
        if not txn_idx == last_txn_idx:
            # otherwise balance would be duplicated in the 'Please Pay' box
            row[-1] = money(txn['balance'])

        t.row(*row)
        rows_to_keep += 1
        t.row_style('LINEBELOW', 0, -1, 0.25, colors.lightgrey)

        t.keep_previous_n_rows_together(rows_to_keep)

    t.row('', '', '', _('Please Pay'), ' '+money(invoice['balance_gross']))
    t.row_style('FONTNAME', 0, -1, font.bold)
    t.row_style('LINEABOVE', -1, -1, 0.5, colors.black)
    t.row_style('LINEBELOW', -1, -1, 0.5, colors.black)
    t.row_style('LINEAFTER', -2, -1, 0.5, colors.black)
    [t.row_style(side+'PADDING', -2, -1, 5) for side in ['LEFT', 'RIGHT', 'BOTTOM', 'TOP']]

    return t.get_table(ContinuationTable, repeatRows=1)


def collate_payments(invoice, available_width):

    t = TableFormatter([0, 1, 1, 1], available_width, debug=DEBUG_DOCUMENT)
    t.style.append(('ALIGNMENT', (0, 0), (0, -1), "LEFT"))
    t.style.append(('ALIGNMENT', (1, 0), (-1, -1), "RIGHT"))
    t.style.append(('VALIGN', (0, 0), (-1, -1), "BOTTOM"))
    t.style.append(('RIGHTPADDING', (-1, 0), (-1, -2), 0))
    t.style.append(('LEFTPADDING', (-1, 0), (-1, -2), 0))

    t.style.append(('LINEBELOW', (0, 0), (-1, 0), 0.25, colors.black))
    t.style.append(('LINEABOVE', (0, -1), (-1, -1), 0.25, colors.black))
    t.style.append(('LINEAFTER', (0, 1), (-2, -2), 0.25, colors.black))

    t.row('', _("consideration"), _("tax"), _("gross"))
    t.row_style('FONTNAME', 0, -1, font.bold)

    t.row(_('Project progress'), money(invoice['debited_net']), money(invoice['debited_tax']), money(invoice['debited_gross']))

    last_txn_idx = len(invoice['transactions'])-1
    for txn_idx, txn in enumerate(invoice['transactions']):

        if txn.get('invoice_id', None) == invoice['id']:
            continue

        if txn['type'] == 'payment':
            pay_day = date_format(date(*map(int, txn['date'].split('-'))), use_l10n=True)
            t.row(p(_('Payment on {date}').format(date=pay_day)), money(-txn['net']), money(-txn['tax']), money(txn['payment_applied']))
            if txn['discount_applied']:
                discount_net = round(Decimal(txn['discount_applied']) / (1+TAX_RATE), 2)
                discount_tax = Decimal(txn['discount_applied']) - discount_net
                t.row(p(_('  Discount applied')), money(discount_net), money(discount_tax), money(txn['discount_applied']))
        elif txn['type'] == 'invoice' and txn['invoice_status'] != 'paid':
            invoice_day = date_format(date(*map(int, txn['date'].split('-'))), use_l10n=True)
            invoice_net = Decimal(txn['net']) if txn['net'] else round(Decimal(txn['gross']) / (1+TAX_RATE), 2)
            invoice_tax = Decimal(txn['tax']) if txn['tax'] else Decimal(txn['gross']) - invoice_net
            description = _("{invoice} from {date}").format(invoice=txn['invoice_title'], date=invoice_day)
            t.row(p(description), money(-invoice_net), money(-invoice_tax),  money(-txn['gross']))

    t.row(_('This Invoice'), money(invoice['debit_net']), money(invoice['debit_tax']), money(invoice['debit_gross']))
    t.row_style('RIGHTPADDING', -1, -1, 0)
    t.row_style('FONTNAME', 0, -1, font.bold)

    return t.get_table(ContinuationTable, repeatRows=1)


def has_itemized_debit(debits):
    for debit in debits:
        if not debit['is_flat']:
            return True


def render(invoice, letterhead, format):

    with BytesIO() as buffer:

        table_width, pagesize = calculate_table_width_and_pagesize(letterhead)

        invoice_date = date_format(date(*map(int, invoice['date'].split('-'))), use_l10n=True)

        doc = SystoriDocument(buffer, pagesize=pagesize, debug=DEBUG_DOCUMENT)

        flowables = [

            get_address_label(invoice),

            get_address_label_spacer(invoice),

            heading_and_date(invoice.get('title') or _("Invoice"), invoice_date, table_width, debug=DEBUG_DOCUMENT),

            Spacer(0, 6*mm),

            Paragraph(_("Invoice No.")+" "+invoice['invoice_no'], stylesheet['NormalRight']),
            Paragraph(_("Please indicate the correct invoice number on your payment."),
                      ParagraphStyle('', parent=stylesheet['Small'], alignment=TA_RIGHT)),

            Paragraph(force_break(invoice['header']), stylesheet['Normal']),

            Spacer(0, 4*mm),

            collate_payments(invoice, table_width),

            Spacer(0, 4*mm),

            KeepTogether(Paragraph(force_break(invoice['footer']), stylesheet['Normal']))

        ]

        if has_itemized_debit(invoice['debits']):

            flowables += [

            PageBreak(),

            Paragraph(invoice_date, stylesheet['NormalRight']),

            Paragraph(_("Itemized listing for Invoice No. {}").format(invoice['invoice_no']), stylesheet['h2']),

            Spacer(0, 4*mm),

            collate_tasks(invoice, table_width),

            Spacer(0, 4*mm),

            collate_tasks_total(invoice, table_width),

            ]

        if format == 'print':
            doc.build(flowables, NumberedCanvas, letterhead)
        else:
            doc.build(flowables, LetterheadCanvas.factory(letterhead), letterhead)

        return buffer.getvalue()


def serialize(invoice_obj, data):

    contact = invoice_obj.project.billable_contact.contact

    invoice = {

        'version': '1.2',

        'id': invoice_obj.id,

        'title': data['title'],
        'date': data['document_date'],
        'invoice_no': data['invoice_no'],

        'header': data['header'],
        'footer': data['footer'],

        'is_final': data['is_final'],

        'business': contact.business,
        'salutation': contact.salutation,
        'first_name': contact.first_name,
        'last_name': contact.last_name,
        'address': contact.address,
        'postal_code': contact.postal_code,
        'city': contact.city,
        'address_label': contact.address_label,

        # debits created solely as a result of this invoice
        'debit_gross': data['debit_gross'],
        'debit_net': data['debit_net'],
        'debit_tax': data['debit_tax'],

        # all debits for jobs on this invoice (including debit above)
        'debited_gross': data['debited_gross'],
        'debited_net': data['debited_net'],
        'debited_tax': data['debited_tax'],

        # balance for all jobs on this invoice
        'balance_gross': data['balance_gross'],
        'balance_net': data['balance_net'],
        'balance_tax': data['balance_tax'],

        'debits': []
    }

    if data.get('add_terms', False):
        invoice['add_terms'] = True  # TODO: Calculate the terms.

    invoice['transactions'] = get_transactions_for_jobs([d['job'] for d in data['debits']], exclude_transaction=invoice_obj.transaction_id)

    for debit in data['debits']:

        job = debit.pop('job')

        debit.update({
            'job.id': job.id,
            'code': job.code,
            'name': job.name,
            'taskgroups': []
        })
        debit['debit_net'] = round(debit['debit_amount'] / (1+TAX_RATE), 2)
        debit['debit_tax'] = debit['debit_amount'] - debit['debit_net']
        invoice['debits'].append(debit)

        if debit['is_flat']:
            continue

        for taskgroup in job.taskgroups.all():
            taskgroup_dict = {
                'id': taskgroup.id,
                'code': taskgroup.code,
                'name': taskgroup.name,
                'description': taskgroup.description,
                'total': taskgroup.billable_total,
                'tasks': []
            }
            debit['taskgroups'].append(taskgroup_dict)

            for task in taskgroup.tasks.all():
                task_dict = {
                    'id': task.id,
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
                        'id': lineitem.id,
                        'name': lineitem.name,
                        'qty': lineitem.unit_qty,
                        'unit': lineitem.unit,
                        'price': lineitem.price,
                        'price_per': lineitem.price_per_task_unit,
                    }
                    task_dict['lineitems'].append(lineitem_dict)

    return invoice
