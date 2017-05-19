from io import BytesIO
from datetime import date
from decimal import Decimal

from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer, KeepTogether, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.lib.templatetags.customformatting import ubrdecimal, money, ubrdecimal_with_unit

from .style import NumberedSystoriDocument, TableFormatter, ContinuationTable
from .style import chunk_text, force_break, p, b, br, pr
from .style import NumberedLetterheadCanvas, NumberedCanvas
from .style import get_available_width_height_and_pagesize
from .style import heading_and_date, get_address_label, get_address_label_spacer, simpleSplit
from .style import get_items_table, get_totals_table, shorten_name_if_needed
from .font import FontManager

DEBUG_DOCUMENT = True  # Shows boxes in rendered output


def collate_tasks(proposal, only_groups, only_task_names, available_width, font):
    items = get_items_table(available_width, font, DEBUG_DOCUMENT)
    totals = get_totals_table(available_width, font, DEBUG_DOCUMENT)

    description_width = 290.0

    def add_total_to_totals(group, depth):
        cols = ['' for i in range(6)]
        cols[0] = p(group['code'], font)
        cols[1] = p(shorten_name_if_needed(group['name'], 15), font)
        cols[5-depth] = pr(money(group['estimate']), font)
        totals.row(*cols)
        # totals.row_style('SPAN', 1, depth-2)

    def add_total_to_items(group):
        try:
            group_total = group['estimate'].net
        except:
            group_total = group['estimate']

        items.row('', br('∑<sub rise=4>{}</sub>'.format(' ' + group['code']), font), '', '', '',
                  money(group_total))
        items.row_style('FONTNAME', 0, -1, font.bold)
        items.row_style('ALIGNMENT', 0, -2, "RIGHT")
        items.row_style('ALIGNMENT', 0, -1, "RIGHT")
        items.row_style('TOPPADDING', 0, -2, 1)
        items.row_style('RIGHTPADDING', 0, -1, 0)
        items.row_style('SPAN', 1, 4)
        items.row('')

    def add_task(task):

        task_total_column = money(task['estimate'])
        if task['is_provisional']:
            task_total_column = _('Optional')

        if task.get('variant_group'):
            if task['variant_serial'] == 0:
                task['name'] = _('Variant {}.0: {}').format(task['variant_group'], task['name'])
            else:
                task['name'] = _('Variant {}.{}: {} - Alternative for Variant {}.0').format(
                    task['variant_group'], task['variant_serial'], task['name'], task['variant_group'])
                task_total_column = _('Alternative')

        items.row(p(task['code'], font), p(task['name'], font))
        items.row_style('SPAN', 1, -2)
        if not only_task_names:
            lines = simpleSplit(task['description'], font.normal.fontName, items.font_size, description_width)
            for line in lines:
                items.row('', p(line, font))
                items.row_style('SPAN', 1, -1)
                items.row_style('TOPPADDING', 0, -1, 1)

        if task['qty'] is not None:
            items.row('', '', ubrdecimal(task['qty']), p(task['unit'], font), money(task['price']), task_total_column)
            items.row_style('ALIGNMENT', 1, -1, "RIGHT")
            items.row_style('BOTTOMPADDING', 0, -1, 10)
        else:
            for li in task['lineitems']:
                items.row('', p(li['name'], font), ubrdecimal(li['qty']), p(li['unit'], font), money(li['price']), money(li['estimate']))
                items.row_style('ALIGNMENT', 1, -1, "RIGHT")
                items.row_style('BOTTOMPADDING', 0, -1, 10)

    def traverse(parent, depth, only_groups, only_task_names, len_groups=1):
        items.row(b(parent['code'], font), b(parent['name'], font))
        items.row_style('SPAN', 1, -1)

        if not only_task_names:
            lines = simpleSplit(parent['description'], font.normal.fontName, items.font_size, description_width)
            for line in lines:
                items.row('', p(line, font))
                items.row_style('SPAN', 1, -1)
                items.row_style('TOPPADDING', 0, -1, 1)
            items.row_style('BOTTOMPADDING', 0, -1, 10)

        if not only_groups:
            for task in parent['tasks']:
                add_task(task)

        for group in parent.get('groups', []):
            traverse(group, depth + 1, only_groups, only_task_names)
            add_total_to_items(group)
            add_total_to_totals(group, depth+1)


    for job in proposal['jobs']:
        len_groups = len(job['groups'])

        items.row(b(job['code'], font), b(job['name'], font))
        items.row_style('SPAN', 1, -1)
        if job.get('description', False):
            items.row('', p(job['description'], font))
            items.row_style('SPAN', 1, -1)

        for group in job.get('groups', []):
            traverse(group, 1, only_groups, only_task_names, len_groups)
            if len_groups > 1:
                add_total_to_items(group)
                add_total_to_totals(group, 1)

        if not only_groups:
            for task in job.get('tasks', []):  # support old JSON
                add_task(task)

        if len(proposal['jobs']) > 1:
            add_total_to_items(job)
        totals.row(b(job['code'], font), b(job['name'], font), '', '', '', money(job['estimate'].net))
        totals.row_style('SPAN', 1, 4)

    totals.row_style('LINEBELOW', 0, -1, 0.25, colors.black)
    totals.row('', _("Total without VAT"), '', '', '', money(proposal['estimate_total'].net))
    totals.row_style('SPAN', 1, 4)
    totals.row('', "19,00% "+_("VAT"), '', '', '', money(proposal['estimate_total'].tax))
    totals.row_style('SPAN', 1, 4)
    totals.row('', _("Total including VAT"), '', '', '', money(proposal['estimate_total'].gross))
    totals.keep_previous_n_rows_together(4)
    totals.row_style('SPAN', 1, 4)

    return [
        items.get_table(ContinuationTable, repeatRows=1),
        totals.get_table()
    ]


def collate_lineitems(proposal, available_width, font):

    pages = []

    def add_task(task):
        pages.append(PageBreak())

        t = TableFormatter([1, 0], available_width, font, debug=DEBUG_DOCUMENT)
        t.style.append(('LEFTPADDING', (0, 0), (-1, -1), 0))
        t.style.append(('RIGHTPADDING', (-1, 0), (-1, -1), 0))
        t.style.append(('VALIGN', (0, 0), (-1, -1), 'TOP'))

        t.row(b(job['code'], font), b(job['name'], font))
        t.row(p(task['code'], font), p(task['name'], font))

        for chunk in chunk_text(task['description']):
            t.row('', p(chunk, font))

        pages.append(t.get_table(ContinuationTable))

        t = TableFormatter([0, 1, 1, 1, 1], available_width, font, debug=DEBUG_DOCUMENT)
        t.style.append(('LEFTPADDING', (0, 0), (-1, -1), 0))
        t.style.append(('RIGHTPADDING', (-1, 0), (-1, -1), 0))
        t.style.append(('VALIGN', (0, 0), (-1, -1), 'TOP'))
        t.style.append(('ALIGNMENT', (1, 0), (1, -1), 'RIGHT'))
        t.style.append(('ALIGNMENT', (3, 0), (-1, -1), 'RIGHT'))

        task_price = Decimal('0')
        for lineitem in task['lineitems']:
            lineitem_qty = ubrdecimal_with_unit(lineitem['qty'], lineitem['unit'])
            t.row(p(lineitem['name'], font),
                  lineitem_qty,
                  p(lineitem['unit'], font),
                  money(lineitem['price']),
                  money(lineitem['estimate'])
                  )
            task_price += lineitem['estimate']

        t.row_style('LINEBELOW', 0, -1, 0.25, colors.black)

        task_qty = ubrdecimal_with_unit(Decimal('1'), task['unit']) if task['qty']\
            else ubrdecimal_with_unit(Decimal('0'), task['unit'])
        t.row('', task_qty, b(task['unit'], font), '', money(task_price))

        t.row_style('FONTNAME', 0, -1, font.bold)

        pages.append(t.get_table(ContinuationTable))

    def traverse(parent, depth):
        for group in parent.get('groups', []):
            traverse(group, depth + 1)

        for task in parent['tasks']:
            add_task(task)

    for job in proposal['jobs']:

        for group in job.get('groups', []):
            traverse(group, 1)

        for task in job.get('tasks', []):
            add_task(task)

    return pages


def render(proposal, letterhead, with_lineitems, only_groups, only_task_names, title, format):

    with BytesIO() as buffer:

        font = FontManager(letterhead.font)

        available_width, available_height, pagesize = get_available_width_height_and_pagesize(letterhead)

        proposal_date = date_format(date(*map(int, proposal['document_date'].split('-'))), use_l10n=True)

        doc = NumberedSystoriDocument(buffer, pagesize=pagesize, debug=DEBUG_DOCUMENT)

        flowables = [

            get_address_label(proposal, font),

            get_address_label_spacer(proposal),

            heading_and_date(proposal['title'], proposal_date, font,
                             available_width, debug=DEBUG_DOCUMENT),
        ]

        if proposal['show_project_id']:
            flowables += [Paragraph(_("Project") + " #" + str(proposal['project_id']), font.normal), ]

        flowables += [
            Spacer(0, 4*mm),

            Paragraph(force_break(proposal['header']), font.normal),

            Spacer(0, 4*mm)

        ] + collate_tasks(proposal, only_groups, only_task_names, available_width, font) + [

            Spacer(0, 10*mm),

            KeepTogether(Paragraph(force_break(proposal['footer']), font.normal)),

        ] + (collate_lineitems(proposal, available_width, font) if with_lineitems else [])

        if format == 'print':
            doc.build(flowables, title, NumberedCanvas, letterhead)
        else:
            doc.build(flowables, title, NumberedLetterheadCanvas.factory(letterhead), letterhead)

        return buffer.getvalue()


def serialize(proposal):

    if proposal.json['add_terms']:
        pass  # TODO: Calculate the terms.

    for job_data in proposal.json['jobs']:
        job_obj = job_data.pop('job')
        job_data['groups'] = []
        job_data['tasks'] = []
        _serialize(job_data, job_obj)


def _serialize(data, parent):

    for group in parent.groups.all():
        group_dict = {
            'group.id': group.id,
            'code': group.code,
            'name': group.name,
            'description': group.description,
            'estimate': group.estimate,
            'tasks': [],
            'groups': []
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
            'unit': task.unit,
            'price': task.price,
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
