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
from reportlab.platypus import BaseDocTemplate, SimpleDocTemplate, Paragraph, Table,\
    TableStyle, Frame, PageTemplate, FrameBreak
from reportlab.platypus import Spacer, cleanBlockQuotedText
from reportlab.platypus.tables import IdentStr
from reportlab.platypus.flowables import KeepTogether
from reportlab.lib import colors

from django.conf import settings
from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.lib.templatetags.customformatting import ubrdecimal, money
from systori.apps.accounting.utils import get_transactions_table

from .style import NumberedCanvas, stylesheet, force_break, p, b, nr
from . import font


DEBUG_DOCUMENT = True  # Shows boxes in rendered output


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


class InvoiceTable(Table):
    pass


class TableFormatter:

    font = font.normal
    font_size = 10

    def __init__(self, columns, width, pad=5*mm, trim_ends=True):
        assert columns.count(0) == 1, "Must have exactly one stretch column."
        self._maximums = columns.copy()
        self._available_width = width
        self._pad = pad
        self._trim_ends = trim_ends
        self.columns = columns
        self.lines = []
        self.style = [
            ('FONTNAME', (0, 0), (-1, -1), self.font),
            ('FONTSIZE', (0, 0), (-1, -1), self.font_size)
        ]
        if DEBUG_DOCUMENT:
            self.style += [
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black)
            ]

    def get_table(self, **kwargs):
        return InvoiceTable(self.lines, colWidths=self.get_widths(), style=self.style, **kwargs)

    def row(self, *line):
        for i, column in enumerate(self.columns):
            if column != 0 and i < len(line):
                self._maximums[i] = max(self._maximums[i], self.string_width(line[i]))
        self.lines.append(line)

    def string_width(self, txt):
        if isinstance(txt, str):
            return stringWidth(txt, self.font, self.font_size)
        else:
            return stringWidth(txt.text, self.font, self.font_size)

    def get_widths(self):

        widths = self._maximums.copy()

        for i, w in enumerate(widths):
            if w != 0:
                widths[i] += self._pad

        if self._trim_ends:
            trim = self._pad/2
            widths[0] -= trim if widths[0] >= trim else 0
            widths[-1] -= trim if widths[-1] >= trim else 0

        widths[widths.index(0)] = self._available_width - sum(widths)

        return widths

    @property
    def _row_num(self): return len(self.lines)-1

    def row_style(self, name, from_column, to_column, *args):
        self.style.append((name, (from_column, self._row_num), (to_column, self._row_num))+args)

    def keep_previous_n_rows_together(self, n):
        self.style.append(('NOSPLIT', (0, self._row_num-n+1), (0, self._row_num)))

def compile_jobs(jobs, available_width):

    t = TableFormatter([1, 0, 1, 1, 1, 1], available_width)
    t.style.append(('LEFTPADDING', (0, 0), (-1,-1), 0))
    t.style.append(('RIGHTPADDING', (-1, 0), (-1,-1), 0))
    t.style.append(('VALIGN', (0, 0), (-1, -1), 'TOP'))

    t.row(_("Pos."), _("Description"), _("Amount"), '', _("Price"), _("Total"))
    t.row_style('FONTNAME', 0, -1, font.bold)
    t.row_style('ALIGNMENT', 2, 3, "CENTER")
    t.row_style('ALIGNMENT', 4, -1, "RIGHT")
    t.row_style('SPAN', 2, 3)

    for job in jobs:
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

                t.row_style('BOTTOMPADDING', 0, -1, 6)

                t.keep_previous_n_rows_together(2)

            t.row('', b('{} {} - {}'.format(_('Total'), taskgroup['code'], taskgroup['name'])),
                  '', '', '', money(taskgroup['total']))
            t.row_style('SPAN', 1, 4)
            t.row_style('ALIGNMENT', -1, -1, "RIGHT")

            t.row('')


    for job in jobs:
        for taskgroup in job['taskgroups']:
            #lines.append(['', p('Total {} - {}'.format(taskgroup['code'], taskgroup['name'])), p(taskgroup['total'])])
            pass

    return t.get_table(repeatRows=1, ident=IdentStr(''))


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

            Spacer(0, 4*mm),

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
