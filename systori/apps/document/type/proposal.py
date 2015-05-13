import os.path
from io import BytesIO
from datetime import date

from PyPDF2 import PdfFileReader, PdfFileWriter

from reportlab.lib.units import mm
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, KeepTogether
from reportlab.lib import colors

from django.conf import settings
from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.lib.templatetags.customformatting import ubrdecimal, money

from .style import SystoriDocument, TableFormatter, ContinuationTable, stylesheet, force_break, p, b, nr
from . import font

from ...accounting.constants import TAX_RATE


DEBUG_DOCUMENT = False  # Shows boxes in rendered output


def collate_tasks(proposal, available_width):

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

    for job in proposal['jobs']:
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


def collate_tasks_total(proposal, available_width):

    t = TableFormatter([0, 1], available_width, debug=DEBUG_DOCUMENT)
    t.style.append(('RIGHTPADDING', (-1, 0), (-1, -1), 0))
    t.style.append(('LEFTPADDING', (0, 0), (0, -1), 0))
    t.style.append(('FONTNAME', (0, 0), (-1, -1), font.bold))
    t.style.append(('ALIGNMENT', (0, 0), (-1, -1), "RIGHT"))

    for job in proposal['jobs']:
        for taskgroup in job['taskgroups']:
            t.row(b('{} {} - {}'.format(_('Total'), taskgroup['code'], taskgroup['name'])),
                  money(taskgroup['total']))
    t.row_style('LINEBELOW', 0, 1, 0.25, colors.black)

    t.row(_("Total without VAT"), money(proposal['total_base']))
    t.row("19,00% "+_("VAT"), money(proposal['total_tax']))
    t.row(_("Total including VAT"), money(proposal['total_gross']))

    return t.get_table()


def render(proposal):

    with BytesIO() as buffer:

        proposal_date = date_format(date(*map(int, proposal['date'].split('-'))), use_l10n=True)

        doc = SystoriDocument(buffer, debug=DEBUG_DOCUMENT)
        doc.build([

            Paragraph(force_break("""\
            {business}
            z.H. {salutation} {first_name} {last_name}
            {address}
            {postal_code} {city}
            """.format(**proposal)), stylesheet['Normal']),

            Spacer(0, 18*mm),

            Paragraph(proposal_date, stylesheet['NormalRight']),

            Paragraph(force_break(proposal['header']), stylesheet['Normal']),

            Spacer(0, 4*mm),

            collate_tasks(proposal, doc.width),

            collate_tasks_total(proposal, doc.width),

            Spacer(0, 10*mm),

            KeepTogether(Paragraph(force_break(proposal['footer']), stylesheet['Normal'])),

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

    proposal = {

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

        'total_gross': project.estimate_total * (TAX_RATE+1),
        'total_base': project.estimate_total,
        'total_tax': project.estimate_total * TAX_RATE,

        }

    if form.cleaned_data['add_terms']:
        proposal['add_terms'] = True  # TODO: Calculate the terms.

    proposal['jobs'] = []

    for job in form.cleaned_data['jobs']:
        job_dict = {
            'code': job.code,
            'name': job.name,
            'taskgroups': []
        }
        proposal['jobs'].append(job_dict)

        for taskgroup in job.taskgroups:
            taskgroup_dict = {
                'code': taskgroup.code,
                'name': taskgroup.name,
                'total': taskgroup.billable_total,
                'tasks': []
            }
            job_dict['taskgroups'].append(taskgroup_dict)

            for task in taskgroup.tasks:
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

    return proposal
