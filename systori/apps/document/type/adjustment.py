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
from systori.apps.accounting.report import generate_transaction_table
from systori.apps.accounting.constants import TAX_RATE

from .style import NumberedSystoriDocument, TableFormatter, ContinuationTable, stylesheet, force_break, p, b
from .style import NumberedLetterheadCanvas, NumberedCanvas
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


def collate_payments(invoice, available_width, show_payment_details):

    t = TableFormatter([0, 1, 1, 1], available_width, debug=DEBUG_DOCUMENT)
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
            t.row(b(_('This Invoice')), money(-row[1]), money(-row[2]), money(-row[3]))
            t.row_style('LINEABOVE', 0, -1, 0.25, colors.black)
        else:
            t.row(p(title), money(row[1]), money(row[2]), money(row[3]))

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

        table_width, pagesize = calculate_table_width_and_pagesize(letterhead)

        invoice_date = date_format(date(*map(int, invoice['date'].split('-'))), use_l10n=True)

        doc = NumberedSystoriDocument(buffer, pagesize=pagesize, debug=DEBUG_DOCUMENT)

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

            collate_payments(invoice, table_width, show_payment_details),

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
            doc.build(flowables, NumberedLetterheadCanvas.factory(letterhead), letterhead)

        return buffer.getvalue()


def serialize(adjustment_obj, data):
    return {}
