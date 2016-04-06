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
from systori.apps.accounting.models import Entry
from systori.apps.accounting.report import create_invoice_report, create_invoice_table
from systori.apps.accounting.constants import TAX_RATE

from .style import NumberedSystoriDocument, TableFormatter, ContinuationTable, fonts, force_break, p, b
from .style import NumberedLetterheadCanvas, NumberedCanvas
from .style import calculate_table_width_and_pagesize
from .style import heading_and_date, get_address_label, get_address_label_spacer
from .font import FontManager


DEBUG_DOCUMENT = False  # Shows boxes in rendered output


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

    table = create_invoice_table(invoice)[1:]
    last_idx = len(table) - 1
    for idx, row in enumerate(table):
        txn = row[4]

        if row[0] == 'progress':
            title = _('Project progress')
        elif row[0] == 'payment':
            pay_day = date_format(date(*map(int, txn['date'].split('-'))), use_l10n=True)
            title = _('Payment on {date}').format(date=pay_day)
        elif row[0] == 'discount':
            title = _('Discount applied')
        elif row[0] == 'unpaid':
            title = _('Open claim from prior invoices')
        elif row[0] == 'debit':
            title = _('This Invoice')
        else:
            raise NotImplementedError()

        t.row(p(title, font), money(row[1]), money(row[2]), money(row[3]))

        if idx == last_idx:
            t.row_style('LINEABOVE', 0, -1, 0.25, colors.black)

        def small_row(*args):
            t.row(*[Paragraph(c, font.small_right) for c in args])

        if show_payment_details and row[0] == 'payment':
            for job in txn['jobs'].values():
                small_row(job['name'], money(job['payment_applied_net']), money(job['payment_applied_tax']), money(job['payment_applied_gross']))

        if show_payment_details and row[0] == 'discount':
            for job in txn['jobs'].values():
                small_row(job['name'], money(job['discount_applied_net']), money(job['discount_applied_tax']), money(job['discount_applied_gross']))


    t.row_style('RIGHTPADDING', -1, -1, 0)
    t.row_style('FONTNAME', 0, -1, font.bold)

    return t.get_table(ContinuationTable, repeatRows=1)


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

    for job in invoice['jobs']:

        items.row(b(job['code'], font), b(job['name'], font))
        items.row_style('SPAN', 1, -1)

        taskgroup_subtotals_added = False

        if job['invoiced'].gross == job['progress'].gross:

            for taskgroup in job['taskgroups']:
                items.row(b(taskgroup['code'], font), b(taskgroup['name'], font))
                items.row_style('SPAN', 1, -1)
                items.keep_next_n_rows_together(2)

                for task in taskgroup['tasks']:
                    items.row(p(task['code'], font), p(task['name'], font))
                    items.row_style('SPAN', 1, -2)

                    items.row('', '', ubrdecimal(task['complete']), p(task['unit'], font), money(task['price']),
                              money(task['total']))
                    items.row_style('ALIGNMENT', 1, -1, "RIGHT")
                    items.keep_previous_n_rows_together(2)

                items.row('', b('{} {} - {}'.format(_('Total'), taskgroup['code'], taskgroup['name']), font),
                          '', '', '', money(taskgroup['total']))
                items.row_style('FONTNAME', 0, -1, font.bold)
                items.row_style('ALIGNMENT', -1, -1, "RIGHT")
                items.row_style('SPAN', 1, 4)
                items.row_style('VALIGN', 0, -1, "BOTTOM")

                items.row('')

                if len(invoice['jobs']) == 1:
                    totals.row(b('{} {} - {}'.format(_('Total'), taskgroup['code'], taskgroup['name']), font),
                               money(taskgroup['total']))
                    taskgroup_subtotals_added = True

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

        if not taskgroup_subtotals_added:
            # taskgroup subtotals are added if there is only 1 job *and* it is itemized
            # in all other cases we're going to show the job total
            totals.row(b('{} {} - {}'.format(_('Total'), job['code'], job['name']), font), money(job['invoiced'].net))

    totals.row_style('LINEBELOW', 0, 1, 0.25, colors.black)
    totals.row(_("Total without VAT"), money(invoice['invoiced'].net))

    return [
        items.get_table(ContinuationTable, repeatRows=1),
        Spacer(0, 4*mm),
        totals.get_table()
    ]


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

            KeepTogether(Paragraph(force_break(invoice['footer']), fonts['OpenSans']['Normal'])),

            # Itemized Listing

            PageBreak(),

            Paragraph(invoice_date, fonts['OpenSans']['NormalRight']),

            Paragraph(_("Itemized listing for Invoice No. {}").format(invoice['invoice_no']),
                      fonts['OpenSans']['h2']),

            Spacer(0, 4*mm),

        ] + collate_itemized_listing(invoice, font, table_width)

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

        'jobs': []

    }

    if data.get('add_terms', False):
        invoice['add_terms'] = True  # TODO: Calculate the terms.

    job_objs = []
    for job_data in data['jobs']:

        job_obj = job_data.pop('job')
        job_objs.append(job_obj)

        job_data.update({
            'job.id': job_obj.id,
            'code': job_obj.code,
            'name': job_obj.name,
            'taskgroups': []
        })
        invoice['jobs'].append(job_data)

        for taskgroup in job_obj.taskgroups.all():
            taskgroup_dict = {
                'id': taskgroup.id,
                'code': taskgroup.code,
                'name': taskgroup.name,
                'description': taskgroup.description,
                'total': taskgroup.progress_total,
                'tasks': []
            }
            job_data['taskgroups'].append(taskgroup_dict)

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

    invoice.update(create_invoice_report(invoice_obj.transaction, job_objs))

    return invoice
