import os

from io import BytesIO
from datetime import date
from decimal import Decimal

from reportlab.lib.units import mm
from reportlab.platypus import Spacer, KeepTogether, PageBreak

from django.conf import settings
from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.lib.templatetags.customformatting import ubrdecimal, money

from .style import NumberedSystoriDocument
from .style import force_break
from .style import NumberedLetterheadCanvas, NumberedCanvas
from .style import get_available_width_height_and_pagesize
from .style import heading_and_date, get_address_label, get_address_label_spacer
from .font import FontManager

from bericht.pdf import PDFStreamer
from bericht.html import HTMLParser, CSS
from django.template.loader import render_to_string


def render_task(task, only_task_names=False):

    kwargs = {
        'task_name': task['name'],
        'task_total': money(task['estimate']),
        'show_description': not only_task_names,
    }
    kwargs.update(task)

    if task['is_provisional']:
        kwargs['task_total'] = _('Optional')

    if task.get('variant_group'):
        if task['variant_serial'] == 0:
            kwargs['task_name'] = _('Variant {}.0: {}').format(task['variant_group'], kwargs['task_name'])
        else:
            kwargs['task_name'] = _('Variant {}.{}: {} - Alternative for Variant {}.0').format(
                task['variant_group'], task['variant_serial'], kwargs['task_name'], task['variant_group'])
            kwargs['task_total'] = _('Alternative')

    return render_to_string('document/proposal_task.html', kwargs)


def render_group(group, depth, only_task_names=False, only_groups=False):
    kwargs = {
        'bold_name': depth <= 2,
        'show_description': depth <= 2 or not only_task_names,
    }
    kwargs.update(group)

    yield render_to_string('document/proposal_group.html', kwargs)

    if not only_groups:
        for task in group.get('tasks', []):
            yield render_task(task, only_task_names)

    for subgroup in group.get('groups', []):
        yield from render_group(subgroup, depth+1, only_groups, only_task_names)

    if not group.get('groups', []) and group.get('tasks', []):
        yield render_to_string('document/proposal_subtotal.html', kwargs)


def html_gen(proposal, letterhead, with_lineitems, only_groups, only_task_names):
    proposal_date = date_format(date(*map(int, proposal['document_date'].split('-'))), use_l10n=True)

    proposal['doc_date'] = proposal_date
    proposal['longest_code'] = '1.1.1.1'
    proposal['longest_amount'] = '1.000,00'
    proposal['longest_unit'] = 'unit name'
    proposal['longest_price'] = '1.000,00'
    proposal['longest_total'] = '1.000.000,00'

    yield render_to_string('document/proposal_header.html', proposal)

    for job in proposal['jobs']:
        yield from render_group(job, 0, only_groups, only_task_names)

    for job in proposal['jobs']:
        for group in job.get('groups', []):
            yield render_to_string('document/proposal_subtotal.html', group)

    yield render_to_string('document/proposal_footer.html', proposal)


def css_gen(letterhead):
    return render_to_string('document/proposal.css', {
        'letterhead': letterhead
    })


def render(proposal, letterhead, with_lineitems, only_groups, only_task_names, format):
    return PDFStreamer(HTMLParser(
        html_gen(proposal, letterhead, with_lineitems, only_groups, only_task_names),
        CSS(css_gen(letterhead))
    ), os.path.join(settings.MEDIA_ROOT, letterhead.letterhead_pdf.name))


def collate_lineitems(proposal, available_width, font):

    style = Style.default().set(
        font_size=12,
        border_spacing_horizontal=8,
        border_spacing_vertical=8,
    )
    bold = style.set(bold=True)

    pages = []

    def add_task(task):
        pages.append(PageBreak())
        t = TableBuilder([0, 1], style)
        t.row(static(job['code'], bold), parse_html('<p>'+job['name']+'</p>', bold))
        t.row(static(task['code'], style), parse_html('<p>'+task['name']+'</p>', style))
        t.row('', parse_html('<p>'+task['description']+'</p>', style) if task['description'] else '')
        pages.append(t.table)

        t = TableBuilder([1, 0, 0, 0, 0], style)
        task_price = Decimal('0')
        for lineitem in task['lineitems']:
            t.row(
                lineitem['name'],
                ubrdecimal(lineitem['qty']),
                lineitem['unit'],
                money(lineitem['price']),
                money(lineitem['estimate'])
            )
            task_price += lineitem['estimate']

        t.row('', static(ubrdecimal(1.00), bold), static(task['unit'], bold), '', static(money(task_price), bold))

        pages.append(t.table)

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


def old_render(proposal, letterhead, with_lineitems, only_groups, only_task_names, format):

    with BytesIO() as buffer:

        font = FontManager(letterhead.font)

        available_width, available_height, pagesize = get_available_width_height_and_pagesize(letterhead)

        proposal_date = date_format(date(*map(int, proposal['document_date'].split('-'))), use_l10n=True)

        doc = NumberedSystoriDocument(buffer, pagesize=pagesize)

        flowables = [
            get_address_label(proposal, font),
            get_address_label_spacer(proposal),
            heading_and_date(proposal['title'], proposal_date, font, available_width),
        ]

        if proposal['show_project_id']:
            flowables += [para(_("Project") + " #" + str(proposal['project_id']))]

        flowables += [
            Spacer(0, 4*mm),
            parse_html('<p>'+force_break(proposal['header'])+'</p>')[0],
            Spacer(0, 4*mm)
        ] + collate_tasks(proposal, only_groups, only_task_names, font, available_width) + [
            Spacer(0, 10*mm),
            KeepTogether(parse_html('<p>'+force_break(proposal['footer'])+'</p>')[0]),
        ] + (collate_lineitems(proposal, available_width, font) if with_lineitems else [])

        if format == 'print':
            doc.build(flowables, NumberedCanvas, letterhead)
        else:
            doc.build(flowables, NumberedLetterheadCanvas.factory(letterhead), letterhead)

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
