from io import BytesIO
from datetime import date
from decimal import Decimal

from reportlab.lib.units import mm
from reportlab.platypus import Spacer, KeepTogether, PageBreak
from reportlab.lib import colors

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.lib.templatetags.customformatting import ubrdecimal, money

from .style import NumberedSystoriDocument, TableFormatter, ContinuationTable
from .style import chunk_text, force_break, p, b, br
from .style import NumberedLetterheadCanvas, NumberedCanvas
from .style import get_available_width_height_and_pagesize
from .style import heading_and_date, get_address_label, get_address_label_spacer, simpleSplit
from .font import FontManager

from bericht.html import parse_html
from bericht.text import Paragraph
from bericht.table import TableBuilder, Cell, Span
from bericht.style import Style, TextAlign


DEBUG_DOCUMENT = False  # Shows boxes in rendered output


class ProposalBuilder(TableBuilder):
    def __init__(self):
        style = Style.default().set(font_size=12)
        super().__init__([1, 0, 1, 1, 1, 1], style)
        self.bold = style.set(bold=True)
        self.padded_row = style.set(padding_bottom=10)
        self.right = style.set(text_align=TextAlign.right)

    def header(self, *cols):
        self.row(*(
            text if isinstance(text, Span)
            else Paragraph.from_string(text, self.bold.set(text_align=alignment))
            for text, alignment in cols
        ))

    def code_name(self, code, name, bold=False):
        self.row(
            Paragraph.from_string(code, self.bold if bold else self.style),
            Paragraph.from_string(name, self.bold if bold else self.style),
            Span.col, Span.col, Span.col, Span.col
        )

    def description(self, html):
        self.row(
            '', parse_html('<p>'+html+'</p>'),
            Span.col, Span.col, Span.col, Span.col,
            #row_style=self.padded_row
        )

    def detail(self, name, qty, unit, price, total):
        self.row(
            '', name,
            Paragraph.from_string(ubrdecimal(qty), self.right),
            unit,
            Paragraph.from_string(money(price), self.right),
            Paragraph.from_string(total, self.right),
            #row_style=self.padded_row
        )


def collate_tasks(proposal, only_groups, only_task_names, font, available_width):
    tbl = ProposalBuilder()
    items = TableFormatter([1, 0, 1, 1, 1, 1], available_width, font, debug=DEBUG_DOCUMENT)
    items.style.append(('LEFTPADDING', (0, 0), (-1, -1), 0))
    items.style.append(('RIGHTPADDING', (-1, 0), (-1, -1), 0))
    items.style.append(('VALIGN', (0, 0), (-1, -1), 'TOP'))

    items.style.append(('LINEABOVE', (0, 'splitfirst'), (-1, 'splitfirst'), 0.25, colors.black))

    tbl.header(
        (_("Pos."), TextAlign.left),
        (_("Description"), TextAlign.left),
        (_("Amount"), TextAlign.center),
        (Span.col, None),
        (_("Price"), TextAlign.right),
        (_("Total"), TextAlign.right),
    )

    # Totals Table
    totals = TableFormatter([0, 1], available_width, font, debug=DEBUG_DOCUMENT)
    totals.style.append(('RIGHTPADDING', (-1, 0), (-1, -1), 0))
    totals.style.append(('LEFTPADDING', (0, 0), (0, -1), 0))
    totals.style.append(('FONTNAME', (0, 0), (-1, -1), font.bold.fontName))
    totals.style.append(('ALIGNMENT', (0, 0), (-1, -1), "RIGHT"))
    totals.row('', '')
    if DEBUG_DOCUMENT:
        items.style.append(('GRID', (0, 0), (-1, -1), 0.5, colors.grey))
        totals.style.append(('GRID', (0, 0), (-1, -1), 0.5, colors.grey))

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

        tbl.code_name(task['code'], task['name'])
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
                items.row('', b('{} {} - {}'.format(_('Total'), group['code'], group['name']), font),
                          '', '', '', money(group['estimate']))
                items.row_style('FONTNAME', 0, -1, font.bold)
                items.row_style('ALIGNMENT', -1, -1, "RIGHT")
                items.row_style('SPAN', 1, 4)
                items.row_style('VALIGN', 0, -1, "BOTTOM")
                items.row('')

        if not only_groups:
            for task in parent['tasks']:
                add_task(task)

    for job in proposal['jobs']:
        tbl.code_name(job['code'], job['name'], bold=True)
        tbl.description(job['description'])
        for group in job.get('groups', []):
            traverse(group, 1, only_groups, only_task_names)
            if not group.get('groups', []) and group.get('tasks', []):
                items.row('', b('{} {} - {}'.format(_('Total'), group['code'], group['name']), font),
                          '', '', '', money(group['estimate']))
                items.row_style('FONTNAME', 0, -1, font.bold)
                items.row_style('ALIGNMENT', -1, -1, "RIGHT")
                items.row_style('SPAN', 1, 4)
                items.row_style('VALIGN', 0, -1, "BOTTOM")
                items.row('')
            totals.row(b('{} {} - {}'.format(_('Total'), group['code'], group['name']), font),
                       money(group['estimate']))

        if not only_groups:
            for task in job.get('tasks', []):  # support old JSON
                add_task(task)

    totals.row_style('LINEBELOW', 0, 1, 0.25, colors.black)
    totals.row(_("Total without VAT"), money(proposal['estimate_total'].net))
    totals.row("19,00% "+_("VAT"), money(proposal['estimate_total'].tax))
    totals.row(_("Total including VAT"), money(proposal['estimate_total'].gross))

    return [
        tbl.table,
        #items.get_table(ContinuationTable, repeatRows=1),
        #totals.get_table()
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
        #t.row(b(taskgroup['code'], font), b(taskgroup['name'], font))
        t.row(p(task['code'], font), p(task['name'], font))

        for chunk in chunk_text(task['description']):
            t.row('', p(chunk, font))

        # t.row_style('BOTTOMPADDING', 0, -1, 10)  seems to have no effect @elmcrest 09/2015

        pages.append(t.get_table(ContinuationTable))

        t = TableFormatter([0, 1, 1, 1, 1], available_width, font, debug=DEBUG_DOCUMENT)
        t.style.append(('LEFTPADDING', (0, 0), (-1, -1), 0))
        t.style.append(('RIGHTPADDING', (-1, 0), (-1, -1), 0))
        t.style.append(('VALIGN', (0, 0), (-1, -1), 'TOP'))
        t.style.append(('ALIGNMENT', (1, 0), (1, -1), 'RIGHT'))
        t.style.append(('ALIGNMENT', (3, 0), (-1, -1), 'RIGHT'))

        task_price = Decimal('0')
        for lineitem in task['lineitems']:
            t.row(p(lineitem['name'], font),
                  ubrdecimal(lineitem['qty']),
                  p(lineitem['unit'], font),
                  money(lineitem['price']),
                  money(lineitem['estimate'])
                  )
            task_price += lineitem['estimate']

        t.row_style('LINEBELOW', 0, -1, 0.25, colors.black)

        t.row('', ubrdecimal(1.00), b(task['unit'], font), '', money(task_price))
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


def render(proposal, letterhead, with_lineitems, only_groups, only_task_names, format):

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
            flowables += [Paragraph.from_string(_("Project") + " #" + str(proposal['project_id'])), ]

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
