from io import BytesIO
from datetime import date

from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib import colors

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.lib.templatetags.customformatting import ubrdecimal, money

from .style import SystoriDocumentWithoutFirstPage, stylesheet, force_break, ContinuationTable, TableFormatter, p, b
from .style import PortraitStationaryCanvasWithoutFirstPage
#from .invoice import collate_tasks, collate_tasks_total
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

def render(project, format):

    with BytesIO() as buffer:

        contact = project.billable_contact.contact
        today = date_format(date.today(), use_l10n=True)

        itemized_listing = {
            'version': '1.0',

            'project_name': project.name,

            'business': contact.business,
            'salutation': contact.salutation,
            'first_name': contact.first_name,
            'last_name': contact.last_name,
            'address': contact.address,
            'postal_code': contact.postal_code,
            'city': contact.city,
            'address_label': contact.address_label,

            'total_gross': project.billable_gross_total,
            'total_base': project.billable_total,
            'total_tax': project.billable_tax_total,
        }

        itemized_listing['jobs'] = []

        for job in project.billable_jobs:
            job_dict = {
                'code': job.code,
                'name': job.name,
                'taskgroups': []
            }
            itemized_listing['jobs'].append(job_dict)

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

        doc = SystoriDocumentWithoutFirstPage(buffer, debug=DEBUG_DOCUMENT)

        flowables = [

            Paragraph(_("Itemized listing {}").format(date.today), stylesheet['h2']),

            Paragraph(_("Project") + ": {}".format(itemized_listing['project_name']), stylesheet['Normal']),
            Paragraph(_("Date") + ": {}".format(today), stylesheet['Normal']),

            Spacer(0, 10*mm),

            collate_tasks(itemized_listing, doc.width),

            Spacer(0, 4*mm),

            collate_tasks_total(itemized_listing, doc.width),

            ]

        if format == 'print':
            doc.build(flowables)
        else:
            doc.build(flowables, canvasmaker=PortraitStationaryCanvasWithoutFirstPage)


        return buffer.getvalue()
