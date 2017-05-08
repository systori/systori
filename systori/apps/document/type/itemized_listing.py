from io import BytesIO
from datetime import date
from decimal import Decimal

from reportlab.lib.units import mm
from reportlab.lib.pagesizes import landscape
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Spacer

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.apps.accounting.constants import TAX_RATE
from systori.lib.templatetags.customformatting import money, ubrdecimal

from .style import NumberedSystoriDocument, fonts, TableFormatter, ContinuationTable
from .style import NumberedLetterheadCanvasLetterheadPageTwo, NumberedCanvas
from .style import get_available_width_height_and_pagesize, b, p, br, pr
from .font import FontManager

DEBUG_DOCUMENT = False  # Shows boxes in rendered output

def collate_itemized_listing(project, total_progress, font, available_width):

    # Itemized Listing Table
    items = TableFormatter([1, 0, 1, 1, 1, 1], available_width, font, debug=DEBUG_DOCUMENT)
    items.style.append(('LEFTPADDING', (0, 0), (-1, -1), 0))
    items.style.append(('RIGHTPADDING', (-1, 0), (-1, -1), 0))
    items.style.append(('RIGHTPADDING', (-2, 0), (-1, -2), 0))
    items.style.append(('VALIGN', (0, 0), (-1, -1), 'TOP'))
    items.style.append(('LINEABOVE', (0, 'splitfirst'), (-1, 'splitfirst'), 0.25, colors.black))

    items.row(_("Pos."), _("Description"), _("Amount"), '', _("Price"), _("Total"))
    items.row_style('ALIGNMENT', 2, -1, "RIGHT")

    # Totals Table
    totals = TableFormatter([1, 0, 1, 1, 1, 1], available_width, font, debug=DEBUG_DOCUMENT)
    totals.style.append(('RIGHTPADDING', (-1, 0), (-1, -1), 0))
    totals.style.append(('LEFTPADDING', (0, 0), (0, -1), 0))
    totals.style.append(('FONTNAME', (0, 0), (-1, -1), font.bold.fontName))
    totals.style.append(('ALIGNMENT', (0, 0), (-1, -1), "RIGHT"))
    totals.row()
    totals.row_style('LINEBELOW', 0, -1, 0.25, colors.black)


    def add_total_to_totals(group):
        totals.row(p(group.code, font), p(group.name[:20] + ' ...', font), '', '', pr(money(group.estimate), font), '')
        totals.row_style('SPAN', 1, 3)

    def add_total_to_items(group):
        items.row('', br('∑<sub rise=4>{}</sub>'.format(' ' + group.code), font), '', '', '', money(group.progress))
        items.row_style('FONTNAME', 0, -1, font.bold)
        items.row_style('ALIGNMENT', 0, -2, "RIGHT")
        items.row_style('ALIGNMENT', 0, -1, "RIGHT")
        items.row_style('TOPPADDING', 0, -2, 1)
        items.row_style('RIGHTPADDING', 0, -1, 0)
        items.row_style('SPAN', 1, 4)
        items.row('')

    def add_task(task):
        items.row(p(task.code, font), p(task.name, font))
        items.row_style('SPAN', 1, -2)

        if task.qty is not None:
            items.row('', '', ubrdecimal(task.complete), p(task.unit, font), money(task.price), money(task.progress))
            items.row_style('ALIGNMENT', 1, -1, "RIGHT")
            items.keep_previous_n_rows_together(2)
        else:
            items.row('', p(task.description, font))
            items.row_style('SPAN', 1, -1)
            for li in task.lineitems.all():
                items.row('', p(li.name, font), ubrdecimal(li.qty), p(li.unit, font), money(li.price), money(li.total))
                items.row_style('ALIGNMENT', 2, -1, "RIGHT")

    def traverse(parent, depth, len_groups=1):
        items.row(b(parent.code, font), b(parent.name, font))
        items.row_style('SPAN', 1, -1)
        items.keep_next_n_rows_together(2)

        for group in parent.groups.all():
            traverse(group, depth + 1)
            if not group.groups.all() and group.tasks.all():
                add_total_to_items(group)
                if len_groups > 1:
                    add_total_to_totals(group)

        for task in parent.tasks.all():
            add_task(task)

        add_total_to_items(parent)

    for job in project:
        len_groups = len(job.groups.all())

        items.row(b(job.code, font), b(job.name, font))
        items.row_style('SPAN', 1, -1)

        for group in job.groups.all():
            traverse(group, 1)
            if not group.groups.all() and group.tasks.all():
                add_total_to_items(group)
                if len_groups > 1:
                    add_total_to_totals(group)

        for task in job.tasks.all():
            add_task(task)

        totals.row(b('{} {} - {}'.format(_('Total'), job.code, job.name), font), '','','','', money(job.progress))
        totals.row_style('SPAN', 0, 4)

    totals.row_style('LINEBELOW', 0, -1, 0.25, colors.black)
    totals.row(_("Total without VAT"), '','','','', money(total_progress))
    totals.row_style('SPAN', 1, 4)

    return [
        items.get_table(ContinuationTable, repeatRows=1),
        totals.get_table()
    ]


def render(project, letterhead, title, format):

    with BytesIO() as buffer:

        font = FontManager(letterhead.font)
        available_width, available_height, pagesize = get_available_width_height_and_pagesize(letterhead)

        today = date_format(date.today(), use_l10n=True)

        itemized_listing, total_progress = serialize(project)

        doc = NumberedSystoriDocument(buffer, pagesize=pagesize, debug=DEBUG_DOCUMENT)

        flowables = [

            Paragraph(_("Itemized listing {}").format(date.today), fonts['OpenSans']['h2']),

            Paragraph(_("Project") + ": {}".format(project.name), fonts['OpenSans']['Normal']),
            Paragraph(_("Date") + ": {}".format(today), fonts['OpenSans']['Normal']),

            Spacer(0, 10*mm),

        ] + collate_itemized_listing(itemized_listing, total_progress, font, available_width)

        if format == 'print':
            doc.build(flowables, title, NumberedCanvas, letterhead)
        else:
            doc.build(flowables, title, NumberedLetterheadCanvasLetterheadPageTwo.factory(letterhead), letterhead)

        return buffer.getvalue()


def serialize(project):

    job_objs = []
    total_progress = 0
    for index, job_obj in enumerate(project.jobs.all()):
        job_data = {}
        job_objs.append(job_obj)
        job_data['groups'] = []
        job_data['tasks'] = []
        total_progress += job_obj.progress
        _serialize(job_data, job_obj)

    return job_objs, total_progress


def _serialize(data, parent):

    for group in parent.groups.all():
        group_dict = {
            'group.id': group.id,
            'code': group.code,
            'name': group.name,
            'description': group.description,
            'tasks': [],
            'groups': [],
            'progress': group.progress,
            'estimate': group.estimate
        }
        data['groups'].append(group_dict)
        _serialize(group_dict, group)

    for task in parent.tasks.all():
        task_dict = {
            'task.id': task.id,
            'code': task.code,
            'name': task.name,
            'description': task.description,
            'is_provisional': task.is_provisional,
            'variant_group': task.variant_group,
            'variant_serial': task.variant_serial,
            'qty': task.qty,
            'complete': task.complete,
            'unit': task.unit,
            'price': task.price,
            'progress': task.progress,
            'estimate': task.total,
            'lineitems': []
        }
        data['tasks'].append(task_dict)

        for lineitem in task.lineitems.all():
            lineitem_dict = {
                'lineitem.id': lineitem.id,
                'name': lineitem.name,
                'qty': lineitem.qty,
                'unit': lineitem.unit,
                'price': lineitem.price,
                'estimate': lineitem.total,
            }
            task_dict['lineitems'].append(lineitem_dict)
