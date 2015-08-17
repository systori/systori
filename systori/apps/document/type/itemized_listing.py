from io import BytesIO
from datetime import date

from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from .style import SystoriDocument, stylesheet
from .style import PortraitStationaryCanvasWithoutFirstPage
from .invoice import collate_tasks, collate_tasks_total

DEBUG_DOCUMENT = False  # Shows boxes in rendered output

def serialize(project):

    for job in project.billable_jobs:
        job_dict = {
            'code': job.code,
            'name': job.name,
            'taskgroups': []
        }

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

    return job_dict

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

        itemized_listing['jobs'] = [serialize(project)]

        doc = SystoriDocument(buffer, topMargin=39*mm, debug=DEBUG_DOCUMENT)

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
