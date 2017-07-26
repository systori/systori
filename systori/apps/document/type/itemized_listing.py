from io import BytesIO
from datetime import date
from decimal import Decimal

from reportlab.lib.units import mm
from reportlab.lib.pagesizes import landscape
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Spacer

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.apps.accounting.models import Entry
from systori.apps.accounting.constants import TAX_RATE
from systori.lib.templatetags.customformatting import money, ubrdecimal

from .style import NumberedSystoriDocument, TableFormatter, ContinuationTable, fonts, p, b
from .style import NumberedLetterheadCanvasWithoutFirstPage, NumberedCanvas
from .style import get_available_width_height_and_pagesize
from .invoice import serialize

from . import font

DEBUG_DOCUMENT = False  # Shows boxes in rendered output


def collate_itemized_listing(invoice, font, available_width):

    # Itemized Listing Table
    items = TableFormatter([1, 0, 1, 1, 1, 1], available_width, font, debug=DEBUG_DOCUMENT)
    items.style.append(('LEFTPADDING', (0, 0), (-1, -1), 0))
    items.style.append(('RIGHTPADDING', (-1, 0), (-1, -1), 0))
    items.style.append(('VALIGN', (0, 0), (-1, -1), 'TOP'))
    items.style.append(('LINEABOVE', (0, 'splitfirst'), (-1, 'splitfirst'), 0.25, colors.black))

    items.row(_("Pos."), _("Description"), _("Amount"), '', _("Price"), _("Total"))
    items.row_style('ALIGNMENT', 2, -1, "RIGHT")

    # Totals Table
    totals = TableFormatter([0, 1], available_width, font, debug=DEBUG_DOCUMENT)
    totals.style.append(('RIGHTPADDING', (-1, 0), (-1, -1), 0))
    totals.style.append(('LEFTPADDING', (0, 0), (0, -1), 0))
    totals.style.append(('FONTNAME', (0, 0), (-1, -1), font.bold.fontName))
    totals.style.append(('ALIGNMENT', (0, 0), (-1, -1), "RIGHT"))

    if DEBUG_DOCUMENT:
        items.style.append(('GRID', (0, 0), (-1, -1), 0.5, colors.grey))
        totals.style.append(('GRID', (0, 0), (-1, -1), 0.5, colors.grey))

    group_subtotals_added = False

    def add_total(group):
        global group_subtotals_added

        if not group.get('groups') and group.get('tasks'):
            items.row('', b('{} {} - {}'.format(_('Total'), group['code'], group['name']), font),
                      '', '', '', money(group['progress']))
            items.row_style('FONTNAME', 0, -1, font.bold)
            items.row_style('ALIGNMENT', -1, -1, "RIGHT")
            items.row_style('SPAN', 1, 4)
            items.row_style('VALIGN', 0, -1, "BOTTOM")
            items.row('')

            totals.row(b('{} {} - {}'.format(_('Total'), group['code'], group['name']), font), money(group['progress']))
            group_subtotals_added = True

    def add_task(task):
        items.row(p(task['code'], font), p(task['name'], font))
        items.row_style('SPAN', 1, -2)

        if task['qty'] is not None:
            items.row('', '', ubrdecimal(task['complete']), p(task['unit'], font), money(task['price']), money(task['progress']))
            items.row_style('ALIGNMENT', 1, -1, "RIGHT")
            items.keep_previous_n_rows_together(2)
        else:
            items.row('', p(task['description'], font))
            items.row_style('SPAN', 1, -1)
            for li in task['lineitems']:
                items.row('', p(li['name'], font), ubrdecimal(li['qty']), p(li['unit'], font), money(li['price']), money(li['estimate']))
                items.row_style('ALIGNMENT', 2, -1, "RIGHT")

    def traverse(parent, depth):
        items.row(b(parent['code'], font), b(parent['name'], font))
        items.row_style('SPAN', 1, -1)
        items.keep_next_n_rows_together(2)

        for group in parent.get('groups', []):
            traverse(group, depth + 1)
            add_total(group)

        for task in parent.get('tasks', []):
            add_task(task)

        add_total(parent)

    for job in invoice['jobs']:

        items.row(b(job['code'], font), b(job['name'], font))
        items.row_style('SPAN', 1, -1)

        if job['invoiced'].net == job['progress'].net:

            for group in job.get('groups', []):
                traverse(group, 1)

            for task in job.get('tasks', []):
                add_task(task)

        else:

            debits = invoice['job_debits'].get(str(job['job.id']), [])
            for debit in debits:
                entry_date = date_format(date(*map(int, debit['date'].split('-'))), use_l10n=True)
                if debit['entry_type'] == Entry.WORK_DEBIT:
                    title = _('Work completed on {date}').format(date=entry_date)
                elif debit['entry_type'] == Entry.FLAT_DEBIT:
                    title = _('Flat invoice on {date}').format(date=entry_date)
                else:  # adjustment, etc
                    title = _('Adjustment on {date}').format(date=entry_date)
                items.row('', title, '', '', '', money(debit['amount'].net))
                items.row_style('SPAN', 1, -2)
                items.row_style('ALIGNMENT', -1, -1, "RIGHT")

        global group_subtotals_added
        if not group_subtotals_added:
            # taskgroup subtotals are added if there is only 1 job *and* it is itemized
            # in all other cases we're going to show the job total
            totals.row(b('{} {} - {}'.format(_('Total'), job['code'], job['name']), font), money(job['invoiced'].net))

    totals.row(_("Total without VAT"), money(invoice['invoiced'].net))
    totals.row_style('LINEABOVE', 0, 1, 0.25, colors.black)

    return [
        items.get_table(ContinuationTable, repeatRows=1),
        Spacer(0, 4*mm),
        totals.get_table()
    ]


def collate_payments(invoice, available_width):

    t = TableFormatter([0, 1, 1, 1], available_width, debug=DEBUG_DOCUMENT)
    t.style.append(('LEFTPADDING', (0, 0), (0, -1), 0))
    t.style.append(('RIGHTPADDING', (-1, 0), (-1, -1), 0))
    t.style.append(('BOTTOMPADDING', (0, 1), (-1, -1), 3*mm))
    t.style.append(('ALIGNMENT', (0, 0), (0, -1), "LEFT"))
    t.style.append(('ALIGNMENT', (1, 0), (-1, -1), "RIGHT"))
    t.style.append(('VALIGN', (0, 0), (-1, -1), "BOTTOM"))

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
            received_on = date_format(payment['transacted_on'], use_l10n=True)
            row[0] = Paragraph(_('Your Payment on') +' ' + received_on, fonts['OpenSans']['Normal'])
        elif payment['type'] == 'discount':
            row[0] = _('Discount Applied')
        billable_amount += payment['amount']
        t.row(*row)

    t.row(_("Billable Total"), money(billable_amount), money(billable_amount/(TAX_RATE+Decimal('1'))), money(billable_amount/(TAX_RATE+Decimal('1'))*TAX_RATE))

    t.row_style('FONTNAME', 0, -1, font.bold)

    return t.get_table(ContinuationTable, repeatRows=1)


def render(project, letterhead, format):

    with BytesIO() as buffer:
        available_width, available_height, pagesize = get_available_width_height_and_pagesize(letterhead)

        today = date_format(date.today(), use_l10n=True)

        itemized_listing = serialize(project, {})

        doc = NumberedSystoriDocument(buffer, pagesize=pagesize, debug=DEBUG_DOCUMENT)

        flowables = [

            Paragraph(_("Itemized listing {}").format(date.today), fonts['OpenSans']['h2']),

            Paragraph(_("Project") + ": {}".format(project.name), fonts['OpenSans']['Normal']),
            Paragraph(_("Date") + ": {}".format(today), fonts['OpenSans']['Normal']),

            Spacer(0, 10*mm),

            collate_payments(itemized_listing, available_width),

            Spacer(0, 10*mm),

        ] + collate_itemized_listing(itemized_listing, font, available_width)

        if format == 'print':
            doc.build(flowables, NumberedCanvas, letterhead)
        else:
            doc.build(flowables, NumberedLetterheadCanvasWithoutFirstPage.factory(letterhead), letterhead)

        return buffer.getvalue()
