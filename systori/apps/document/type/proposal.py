from io import BytesIO
from datetime import date
from decimal import Decimal

from reportlab.lib.units import mm
from reportlab.platypus import Spacer, KeepTogether, PageBreak

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.lib.templatetags.customformatting import ubrdecimal, money

from .style import NumberedSystoriDocument
from .style import force_break
from .style import NumberedLetterheadCanvas, NumberedCanvas
from .style import get_available_width_height_and_pagesize
from .style import heading_and_date, get_address_label, get_address_label_spacer
from .font import FontManager

from bericht.html import parse_html
from bericht.text import para, static
from bericht.table import TableBuilder, Span
from bericht.style import Style, TextAlign, VerticalAlign


class ProposalBuilder(TableBuilder):
    def __init__(self):
        style = Style.default().set(
            font_size=12,
            border_spacing_horizontal=8,
            border_spacing_vertical=8,
        )
        super().__init__([0, 1, 0, 0, 0, 0], style)
        self.bold = style.set(bold=True)
        self.right = style.set(text_align=TextAlign.right)
        self.bold_right = self.right.set(bold=True)
        self.bottom = style.set(vertical_align=VerticalAlign.bottom)

    def header(self, *cols):
        self.row(*(
            text if isinstance(text, Span)
            else static(text, self.bold.set(text_align=alignment))
            for text, alignment in cols
        ))

    def code_name(self, code, name, bold=False):
        bold = self.bold if bold else self.style
        self.row(
            static(code, bold),
            parse_html('<p>'+name+'</p>', bold)[0],
            Span.col, Span.col, Span.col, Span.col,
        )

    def description(self, html):
        self.row(
            '', parse_html('<p>'+html+'</p>'),
            Span.col, Span.col, Span.col, Span.col,
        )

    def detail(self, name, qty, unit, price, total):
        self.row(
            '', name,
            static(ubrdecimal(qty), self.right),
            unit,
            static(money(price), self.right),
            static(total, self.right),
        )

    def total(self, code, name, total):
        self.row(
            '',
            static('{} {} - {}'.format(_('Total'), code, name), self.bold_right),
            Span.col, Span.col, Span.col,
            static(money(total), self.bold_right),
            cell_style=self.bottom
        )


class TotalBuilder(TableBuilder):
    def __init__(self):
        style = Style.default().set(
            font_size=12,
            border_spacing_horizontal=8,
            border_spacing_vertical=8,
        )
        super().__init__([1, 0], style)
        self.bold = style.set(bold=True)
        self.right = style.set(text_align=TextAlign.right)
        self.bold_right = self.right.set(bold=True)
        self.bottom = style.set(vertical_align=VerticalAlign.bottom)

    def subtotal(self, name, total):
        self.row(
            static(name, self.bold),
            static(money(total), self.bold_right),
            cell_style=self.bottom
        )

    def grand_total(self, name, total):
        self.row(
            para(name, self.bold_right),
            static(money(total), self.bold_right),
            cell_style=self.bottom
        )


def collate_tasks(proposal, only_groups, only_task_names, font, available_width):
    tbl = ProposalBuilder()
    tbl.header(
        (_("Pos."), TextAlign.left),
        (_("Description"), TextAlign.center),
        (_("Amount"), TextAlign.center),
        (Span.col, None),
        (_("Price"), TextAlign.right),
        (_("Total"), TextAlign.right),
    )

    # Totals Table
    totals = TotalBuilder()

    def add_task(task):
        task_name = task['name']
        task_total_column = money(task['estimate'])
        if task['is_provisional']:
            task_total_column = _('Optional')
        if task.get('variant_group'):
            if task['variant_serial'] == 0:
                task_name = _('Variant {}.0: {}').format(task['variant_group'], task_name)
            else:
                task_name = _('Variant {}.{}: {} - Alternative for Variant {}.0').format(
                    task['variant_group'], task['variant_serial'], task_name, task['variant_group'])
                task_total_column = _('Alternative')

        tbl.code_name(task['code'], task_name)
        if not only_task_names:
            tbl.description(task['description'])

        if task['qty'] is not None:
            tbl.detail('', task['qty'], task['unit'], task['price'], task_total_column)
        else:
            for li in task['lineitems']:
                tbl.detail(li['name'], li['qty'], li['unit'], li['price'], money(li['estimate']))

    def traverse(parent, depth, only_groups, only_task_names):
        tbl.code_name(parent['code'], parent['name'], bold=True)
        if not only_task_names:
            tbl.description(parent['description'])
        for group in parent.get('groups', []):
            traverse(group, depth + 1, only_groups, only_task_names)
            if not group.get('groups', []) and group.get('tasks', []):
                tbl.total(group['code'], group['name'], group['estimate'])

        if not only_groups:
            for task in parent['tasks']:
                add_task(task)

    for job in proposal['jobs']:
        tbl.code_name(job['code'], job['name'], bold=True)
        tbl.description(job['description'])
        for group in job.get('groups', []):
            traverse(group, 1, only_groups, only_task_names)
            if not group.get('groups', []) and group.get('tasks', []):
                tbl.total(group['code'], group['name'], group['estimate'])
            totals.subtotal('{} {} - {}'.format(_('Total'), group['code'], group['name']), group['estimate'])

        if not only_groups:
            for task in job.get('tasks', []):  # support old JSON
                add_task(task)

    totals.grand_total(_("Total without VAT"), proposal['estimate_total'].net)
    totals.grand_total("19,00% "+_("VAT"), proposal['estimate_total'].tax)
    totals.grand_total(_("Total including VAT"), proposal['estimate_total'].gross)

    return [tbl.table, totals.table]


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


def render(proposal, letterhead, with_lineitems, only_groups, only_task_names, format):

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
