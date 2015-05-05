from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import BaseDocTemplate, SimpleDocTemplate, Paragraph, Table, TableStyle, Frame, PageTemplate, FrameBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.rl_settings import showBoundary

from django.utils.translation import ugettext as _
from django.http.response import HttpResponse

from systori.apps.accounting.utils import get_transactions_table
from reportlab.platypus.doctemplate import NextPageTemplate, FrameBreak


def txt(t):
    return Paragraph(str(t), ParagraphStyle('',fontName='Helvetica',fontSize=12,leading=17))

def render_old(invoice):

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


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        # Change the position of this to wherever you want the page number to be
        self.drawRightString(190 * mm, 10 * mm,
                             "Page %d of %d" % (self._pageNumber, page_count))

def first_page(canvas, document):
    pass

def later_pages(canvas, document):
    pass

def render(self, invoice):
    with BytesIO() as buffer:

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='centered', fontName='DroidSans', alignment=TA_CENTER))

        recipient = Frame(5 * mm, 282 * mm, 20 * cm, 10 * mm, id='recipient', showBoundary=1)
        content = Frame(5 * mm, 17.5 * mm, 20 * cm, 262 * mm, id='content', showBoundary=1)
        footer = Frame(5 * mm, 5 * mm, 20 * cm, 10 * mm, id='footer', showBoundary=1)

        mainPage = PageTemplate(frames=[recipient, content, footer])

        #doc = BaseDocTemplate(buffer,
        doc = SimpleDocTemplate(buffer,
                              rightMargin=0,
                              leftMargin=0,
                              topMargin=0,
                              bottomMargin=0,
                              pagesize=A4)
        elements = []

        #doc.addPageTemplates([PageTemplate(id='Standard',frames=[recipient, content, footer])])

        #elements.append(NextPageTemplate('Standard'))
        elements.append(Paragraph('This is the Header.', styles['BodyText']))
        #elements.append(FrameBreak())

        elements.append(txt(invoice['business']))

        #elements.append(FrameBreak())
        elements.append(Paragraph('This is the Footer.', styles['BodyText']))

        # but here it's just 'called'?
        # I mean that's what I assume it gets called ... onFirstPage and onLaterPages
        # or it's handed to some other thing
        doc.build(elements, onFirstPage=first_page, onLaterPages=later_pages, canvasmaker=NumberedCanvas)
        #doc.build(elements, canvasmaker=NumberedCanvas)

        return buffer.getvalue()