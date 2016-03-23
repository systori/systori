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
from systori.apps.accounting.report import generate_transaction_table
from systori.apps.accounting.constants import TAX_RATE

from .style import NumberedSystoriDocument, TableFormatter, ContinuationTable, fonts, force_break, p, b
from .style import NumberedLetterheadCanvas, NumberedCanvas
from .style import calculate_table_width_and_pagesize
from .style import heading_and_date, get_address_label, get_address_label_spacer
from .font import FontManager


DEBUG_DOCUMENT = False  # Shows boxes in rendered output


def collate_tasks(invoice, font, available_width):

    t = TableFormatter([1, 0, 1, 1, 1, 1], available_width, font, debug=DEBUG_DOCUMENT)
    t.style.append(('LEFTPADDING', (0, 0), (-1, -1), 0))
    t.style.append(('RIGHTPADDING', (-1, 0), (-1, -1), 0))
    t.style.append(('VALIGN', (0, 0), (-1, -1), 'TOP'))
    t.style.append(('LINEABOVE', (0, 'splitfirst'), (-1, 'splitfirst'), 0.25, colors.black))

    t.row(_("Pos."), _("Description"), _("Amount"), '', _("Price"), _("Total"))

    for job in invoice['jobs']:
        t.row(b(job['code'], font), b(job['name'], font))
        t.row_style('SPAN', 1, -1)

        for taskgroup in job['taskgroups']:
            t.row(b(taskgroup['code'], font), b(taskgroup['name'], font))
            t.row_style('SPAN', 1, -1)
            t.keep_next_n_rows_together(2)

            for task in taskgroup['tasks']:
                t.row(p(task['code'], font), p(task['name'], font))
                t.row_style('SPAN', 1, -2)

                t.row('', '', ubrdecimal(task['complete']), p(task['unit'], font), money(task['price']),
                      money(task['total']))
                t.row_style('ALIGNMENT', 1, -1, "RIGHT")
                t.keep_previous_n_rows_together(2)

            t.row('', b('{} {} - {}'.format(_('Total'), taskgroup['code'], taskgroup['name']), font),
                  '', '', '', money(taskgroup['total']))
            t.row_style('FONTNAME', 0, -1, font.bold)
            t.row_style('ALIGNMENT', -1, -1, "RIGHT")
            t.row_style('SPAN', 1, 4)
            t.row_style('VALIGN', 0, -1, "BOTTOM")

            t.row('')

    return t.get_table(ContinuationTable, repeatRows=1)


def collate_tasks_total(invoice, font, available_width):

    t = TableFormatter([0, 1], available_width, font, debug=DEBUG_DOCUMENT)
    t.style.append(('RIGHTPADDING', (-1, 0), (-1, -1), 0))
    t.style.append(('LEFTPADDING', (0, 0), (0, -1), 0))
    t.style.append(('FONTNAME', (0, 0), (-1, -1), font.bold.fontName))
    t.style.append(('ALIGNMENT', (0, 0), (-1, -1), "RIGHT"))

    for job in invoice['jobs']:
        for taskgroup in job['taskgroups']:
            t.row(b('{} {} - {}'.format(_('Total'), taskgroup['code'], taskgroup['name']), font),
                  money(taskgroup['total']))
    t.row_style('LINEBELOW', 0, 1, 0.25, colors.black)

    t.row(_("Total without VAT"), money(invoice['debited_net']))

    return t.get_table()


def collate_history(invoice, font, available_width):

    t = TableFormatter([0, 1, 1, 1, 1], available_width, font, debug=DEBUG_DOCUMENT)
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


def collate_payments(invoice, font, available_width, show_payment_details):

    t = TableFormatter([0, 1, 1, 1], available_width, font, debug=DEBUG_DOCUMENT)
    t.style.append(('ALIGNMENT', (0, 0), (0, -1), "LEFT"))
    t.style.append(('ALIGNMENT', (1, 0), (-1, -1), "RIGHT"))
    t.style.append(('VALIGN', (0, 0), (-1, -1), "BOTTOM"))
    t.style.append(('RIGHTPADDING', (-1, 0), (-1, -2), 0))
    t.style.append(('LEFTPADDING', (-1, 0), (-1, -2), 0))

    t.style.append(('LINEBELOW', (0, 0), (-1, 0), 0.25, colors.black))
    t.style.append(('LINEAFTER', (0, 1), (-2, -2), 0.25, colors.black))

    t.row('', _("consideration"), _("tax"), _("gross"))
    t.row_style('FONTNAME', 0, -1, font.bold)

    table = generate_transaction_table(invoice)[1:]
    last_idx = len(table) - 1
    for idx, row in enumerate(table):
        txn = row[4]

        if txn is None:
            title = _('Project progress')
        elif row[0] == 'payment':
            pay_day = date_format(date(*map(int, txn['date'].split('-'))), use_l10n=True)
            title = _('Payment on {date}').format(date=pay_day)
        elif row[0] == 'discount':
            title = _('Discount applied')
        elif row[0] == 'invoice':
            invoice_day = date_format(date(*map(int, txn['date'].split('-'))), use_l10n=True)
            title = _("{invoice} from {date}").format(invoice=txn['invoice_title'], date=invoice_day)

        if idx == last_idx:
            t.row(b(_('This Invoice'), font), money(-row[1]), money(-row[2]), money(-row[3]))
            t.row_style('LINEABOVE', 0, -1, 0.25, colors.black)
        else:
            t.row(p(title, font), money(row[1]), money(row[2]), money(row[3]))

        def small_row(*args):
            t.row(*[Paragraph(c, stylesheet['SmallRight']) for c in args])

        if show_payment_details and row[0] == 'payment':
            for job in txn['jobs'].values():
                small_row(job['name'], money(job['payment_applied_net']), money(job['payment_applied_tax']), money(job['payment_applied_gross']))

        if show_payment_details and row[0] == 'discount':
            for job in txn['jobs'].values():
                small_row(job['name'], money(job['discount_applied_net']), money(job['discount_applied_tax']), money(job['discount_applied_gross']))

        if show_payment_details and row[0] == 'invoice':
            for job in txn['jobs'].values():
                unpaid_gross = job['gross'] - job['paid_gross']
                if unpaid_gross > 0:
                    small_row(job['name'], money(-(job['net']-job['paid_net'])), money(-(job['tax']-job['paid_tax'])), money(-unpaid_gross))


    t.row_style('RIGHTPADDING', -1, -1, 0)
    t.row_style('FONTNAME', 0, -1, font.bold)

    return t.get_table(ContinuationTable, repeatRows=1)


def has_itemized_debit(debits):
    for debit in debits:
        if not debit['is_override']:
            return True


def render(invoice, letterhead, show_payment_details, format):

    with BytesIO() as buffer:

        font = FontManager(letterhead.font)
        table_width, pagesize = calculate_table_width_and_pagesize(letterhead)
        invoice_date = date_format(date(*map(int, invoice['date'].split('-'))), use_l10n=True)
        doc = NumberedSystoriDocument(buffer, pagesize=pagesize, debug=DEBUG_DOCUMENT)

        flowables = [

            get_address_label(invoice, font),

            get_address_label_spacer(invoice),

            heading_and_date(invoice.get('title') or _("Invoice"), invoice_date, font, table_width,
                             debug=DEBUG_DOCUMENT),

            Spacer(0, 6*mm),

            Paragraph(_("Invoice No.") + " " + invoice['invoice_no'], font.normal_right),
            Paragraph(_("Please indicate the correct invoice number on your payment."),
                      ParagraphStyle('', parent=fonts['OpenSans']['Small'], alignment=TA_RIGHT)),

            Paragraph(force_break(invoice['header']), fonts['OpenSans']['Normal']),

            Spacer(0, 4*mm),

            collate_payments(invoice, font, table_width, show_payment_details),

            Spacer(0, 4*mm),

            KeepTogether(Paragraph(force_break(invoice['footer']), fonts['OpenSans']['Normal']))

        ]

        if has_itemized_debit(invoice['jobs']):

            flowables += [

                PageBreak(),

                Paragraph(invoice_date, fonts['OpenSans']['NormalRight']),

                Paragraph(_("Itemized listing for Invoice No. {}").format(invoice['invoice_no']),
                          fonts['OpenSans']['h2']),

                Spacer(0, 4*mm),

                collate_tasks(invoice, font, table_width),

                Spacer(0, 4*mm),

                collate_tasks_total(invoice, font, table_width),

            ]

        if format == 'print':
            doc.build(flowables, NumberedCanvas, letterhead)
        else:
            doc.build(flowables, NumberedLetterheadCanvas.factory(letterhead), letterhead)

        return buffer.getvalue()


def serialize(invoice_obj, data):

    contact = invoice_obj.project.billable_contact.contact

    invoice = {

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
        'debit': data['debit'],

        # all debits for jobs on this invoice (including debit above)
        # this is the top 'Project progress' row in history table
        # set later by calling prepare_transaction_report
        'invoiced': data['invoiced'],

        # balance for all jobs on this invoice
        'balance': data['balance'],

        # payment history and prior invoices
        'transactions': [],

        # debits created with this invoice
        # used when 'editing' the invoice and to show itemization table
        'jobs': []

    }

    if data.get('add_terms', False):
        invoice['add_terms'] = True  # TODO: Calculate the terms.

    for debit in data['jobs']:

        job = debit.pop('job')

        debit.update({
            'job.id': job.id,
            'code': job.code,
            'name': job.name,
            'taskgroups': []
        })
        invoice['jobs'].append(debit)

        if debit['is_override']:
            continue

        for taskgroup in job.taskgroups.all():
            taskgroup_dict = {
                'id': taskgroup.id,
                'code': taskgroup.code,
                'name': taskgroup.name,
                'description': taskgroup.description,
                'total': taskgroup.progress_total,
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
                    'total': task.fixed_price_progress,
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
