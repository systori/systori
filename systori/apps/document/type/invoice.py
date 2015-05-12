import os.path
from types import MethodType
from io import BytesIO
from datetime import date

from PyPDF2 import PdfFileReader, PdfFileWriter

from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import BaseDocTemplate, SimpleDocTemplate, Paragraph, Table, TableStyle, Frame, PageTemplate, FrameBreak
from reportlab.platypus import Spacer, cleanBlockQuotedText
from reportlab.platypus.tables import IdentStr
from reportlab.lib import colors

from django.conf import settings
from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.lib.templatetags.customformatting import ubrdecimal, money
from systori.apps.accounting.utils import get_transactions_table

from .style import NumberedCanvas, stylesheet, force_break, p, b, nr
from . import font


DEBUG_DOCUMENT = True # Shows boxes in rendered output


class InvoiceDocument(BaseDocTemplate):

    def __init__(self, buffer):
        super(InvoiceDocument, self).__init__(buffer,
            pagesize = A4,
            topMargin = 55*mm,
            bottomMargin = 22*mm,
            leftMargin = 25*mm,
            rightMargin = 62*mm,
            showBoundary = DEBUG_DOCUMENT
        )

    def onFirstPage(self, canvas, document):
        pass

    def onLaterPages(self, canvas, document):
        pass

    def handle_pageBegin(self):
        self._handle_pageBegin()
        self._handle_nextPageTemplate('Later')

    def build(self, flowables):
        self._calc()
        frame = Frame(self.leftMargin, self.bottomMargin,
                       self.width, self.height,
                       leftPadding=0, bottomPadding=0,
                       rightPadding=0, topPadding=0)
        self.addPageTemplates([
            PageTemplate(id='First', frames=frame, onPage=self.onFirstPage, pagesize=self.pagesize),
            PageTemplate(id='Later', frames=frame, onPage=self.onLaterPages, pagesize=self.pagesize)
        ])
        super(InvoiceDocument, self).build(flowables, canvasmaker=NumberedCanvas)


class ItemizedTable(Table):
    # TODO: Figure out a way to add "Continued..." and "...continued"
    def onSplit(self, table, byRow=1):
        self_pos = int(self.ident[1:-1])
        table_pos = int(table.ident[1:-1])
        if self_pos+1 == table_pos: pos = "Previous"
        if self_pos+2 == table_pos: pos = "Next"
        print(table_pos, self.ident, table.ident)
        #self.canv.setFont(font.normal, 10)
        #self.canv.drawRightString(145*mm, 10*mm, 'Continue..')


def compile_jobs(jobs, available_width):

    lines = []
    def row(): return len(lines)-1
    def s_width(t): return stringWidth(t, font.normal, 10)

    style = [
        ('FONTNAME', (0, 0), (-1, -1), font.normal),
        ('FONTSIZE', (0, 0), (-1, -1), 10)
    ]
    if DEBUG_DOCUMENT:
        style += [
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black)
        ]

    lines.append((_("Pos."), _("Description"), _("Amount"), '', _("Price"), _("Total")))
    style.append(('FONTNAME', (0, row()), (-1, row()), font.bold))
    style.append(('ALIGNMENT', (1, row()), (-1, row()), "CENTER"))
    style.append(('SPAN', (2, row()), (3, row())))

    code_width = 1
    complete_width = 1
    unit_width = 1
    price_width = 1
    total_width = 1

    for job in jobs:
        lines.append([b(job['code']), b(job['name'])])
        code_width = max(code_width, s_width(job['code']))
        style.append(('SPAN', (1, row()), (-1, row())))

        for taskgroup in job['taskgroups']:
            lines.append([b(taskgroup['code']), b(taskgroup['name'])])
            code_width = max(code_width, s_width(taskgroup['code']))
            style.append(('SPAN', (1, row()), (-1, row())))

            for task in taskgroup['tasks']:
                lines.append([p(task['code']), p(task['name'])])
                code_width = max(code_width, s_width(task['code']))
                style.append(('SPAN', (1, row()), (-1, row())))

                s_complete = ubrdecimal(task['complete'])
                s_price = money(task['price'])
                s_total = money(task['total'])

                lines.append(['', '', s_complete, p(task['unit']), s_price, s_total])
                style.append(('ALIGNMENT', (1, row()), (-1, row()), "RIGHT"))

                complete_width = max(complete_width, s_width(s_complete))
                unit_width = max(unit_width, s_width(cleanBlockQuotedText(task['unit'])))
                price_width = max(price_width, s_width(s_price))
                total_width = max(total_width, s_width(s_total))

            s_total = money(taskgroup['total'])
            lines.append(['', b('{} {} - {}'.format(_('Total'), taskgroup['code'], taskgroup['name'])), '', '', '', s_total])
            style.append(('SPAN', (1, row()), (4, row())))
            style.append(('ALIGNMENT', (-1, row()), (-1, row()), "RIGHT"))
            total_width = max(total_width, s_width(s_total))

            lines.append([''*6])  # blank row


    for job in jobs:
        for taskgroup in job['taskgroups']:
            #lines.append(['', p('Total {} - {}'.format(taskgroup['code'], taskgroup['name'])), p(taskgroup['total'])])
            pass

    pad = 5*mm
    widths = [
        code_width + pad,
        0,
        complete_width + pad,
        unit_width + pad,
        price_width + pad,
        total_width + pad
    ]
    widths[1] = available_width - sum(widths)

    return ItemizedTable(lines, colWidths=widths, style=style, repeatRows=1, ident=IdentStr(''))


def compile_payments(invoice):

    lines = [['', nr(invoice['total_gross']), nr(invoice['total_base']), nr(invoice['total_tax'])]]
    for payment in invoice['transactions']:
        row = ['', nr(payment['amount']), nr(payment['amount_base']), nr(payment['amount_tax'])]
        if payment['type'] == 'payment':
            received_on = date_format(date(*map(int, payment['received_on'].split('-'))), use_l10n=True)
            row[0] = p(_('Your Payment on')+' '+received_on)
        elif payment['type'] == 'discount':
            row[0] = p(_('Discount Applied'))
        lines.append(row)

    lines.append(['', nr(invoice['balance_gross']), nr(invoice['balance_base']), nr(invoice['balance_tax'])])

    return lines


def render(invoice):

    with BytesIO() as buffer:

        invoice_date = date_format(date(*map(int, invoice['date'].split('-'))), use_l10n=True)

        doc = InvoiceDocument(buffer)
        doc.build([

            Paragraph(force_break("""\
            {business}
            z.H. {salutation} {first_name} {last_name}
            {address}
            {postal_code} {city}
            """.format(**invoice)), stylesheet['Normal']),

            Spacer(0, 18*mm),

            Paragraph(_("Invoice"), stylesheet['h2']),

            Spacer(0, 4*mm),

            Paragraph(invoice_date, stylesheet['NormalRight']),
            Paragraph(_("Invoice No.")+" "+invoice['invoice_no'], stylesheet['NormalRight']),
            Paragraph(_("Please indicate the correct invoice number on your payment."),
                      ParagraphStyle('', parent=stylesheet['Small'], alignment=TA_RIGHT)),

            Paragraph(force_break(invoice['header']), stylesheet['Normal']),

            Spacer(0, 4*mm),

            compile_jobs(invoice['jobs'], doc.width),

            Table(compile_payments(invoice)),

            Paragraph(force_break(invoice['footer']), stylesheet['Normal']),

        ])

        DIR = os.path.join(settings.BASE_DIR, 'static')

        pdf = PdfFileReader(BytesIO(buffer.getvalue()))
        cover_pdf = PdfFileReader(os.path.join(DIR, "soft_briefbogen_2014.pdf"))

        output = PdfFileWriter()

        for idx, page in enumerate(pdf.pages):
            if idx is 0:
                page.mergePage(cover_pdf.getPage(0))
            else:
                page.mergePage(cover_pdf.getPage(1))
            output.addPage(page)

        with BytesIO() as final_output:
            output.write(final_output)
            return final_output.getvalue()


def serialize(project, form):

    contact = project.billable_contact.contact

    invoice = {

        'version': '1.0',

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
