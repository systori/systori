from io import BytesIO
from datetime import date

from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from reportlab.platypus import Paragraph, Spacer, KeepTogether, PageBreak
from reportlab.lib import colors

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.lib.templatetags.customformatting import ubrdecimal, money

from .style import NumberedSystoriDocument, TableFormatter, ContinuationTable
from .style import chunk_text, force_break, p, b
from .style import NumberedLetterheadCanvas, NumberedCanvas
from .style import calculate_table_width_and_pagesize
from .style import heading_and_date, get_address_label, get_address_label_spacer
from .font import FontManager


DEBUG_DOCUMENT = False  # Shows boxes in rendered output


def collate_tasks(proposal, font, available_width):

    items = TableFormatter([1, 0, 1, 1, 1, 1], available_width, font, debug=DEBUG_DOCUMENT)
    items.style.append(('LEFTPADDING', (0, 0), (-1, -1), 0))
    items.style.append(('RIGHTPADDING', (-1, 0), (-1, -1), 0))
    items.style.append(('VALIGN', (0, 0), (-1, -1), 'TOP'))
    items.style.append(('LINEABOVE', (0, 'splitfirst'), (-1, 'splitfirst'), 0.25, colors.black))

    items.row(_("Pos."), _("Description"), _("Amount"), '', _("Price"), _("Total"))
    items.row_style('FONTNAME', 0, -1, font.bold)
    items.row_style('ALIGNMENT', 2, 3, "CENTER")
    items.row_style('ALIGNMENT', 4, -1, "RIGHT")
    items.row_style('SPAN', 2, 3)

    # Totals Table
    totals = TableFormatter([0, 1], available_width, font, debug=DEBUG_DOCUMENT)
    totals.style.append(('RIGHTPADDING', (-1, 0), (-1, -1), 0))
    totals.style.append(('LEFTPADDING', (0, 0), (0, -1), 0))
    totals.style.append(('FONTNAME', (0, 0), (-1, -1), font.bold.fontName))
    totals.style.append(('ALIGNMENT', (0, 0), (-1, -1), "RIGHT"))

    description_width = 314.0

    for job in proposal['jobs']:

        items.row(b(job['code'], font), b(job['name'], font))
        items.row_style('SPAN', 1, -1)

        taskgroup_subtotals_added = False

        for taskgroup in job['taskgroups']:
            items.row(b(taskgroup['code'], font), b(taskgroup['name'], font))
            items.row_style('SPAN', 1, -1)

            lines = simpleSplit(taskgroup['description'], font.normal.fontName, items.font_size, description_width)

            for line in lines:
                items.row('', p(line, font))
                items.row_style('SPAN', 1, -1)
                items.row_style('TOPPADDING', 0, -1, 1)
            items.row_style('BOTTOMPADDING', 0, -1, 10)

            for task in taskgroup['tasks']:
                items.row(p(task['code'], font), p(task['name'], font))
                items.row_style('SPAN', 1, -2)

                lines = simpleSplit(task['description'], font.normal.fontName, items.font_size, description_width)
                for line in lines:
                    items.row('', p(line, font))
                    items.row_style('SPAN', 1, -1)
                    items.row_style('TOPPADDING', 0, -1, 1)

                task_total_column = money(task['estimate_net'])
                if task['is_optional']:
                    task_total_column = _('Optional')
                elif not task['selected']:
                    task_total_column = _('Alternative')

                items.row('', '', ubrdecimal(task['qty']), p(task['unit'], font), money(task['price']), task_total_column)
                items.row_style('ALIGNMENT', 1, -1, "RIGHT")
                items.row_style('BOTTOMPADDING', 0, -1, 10)

            items.row('', b('{} {} - {}'.format(_('Total'), taskgroup['code'], taskgroup['name']), font),
                  '', '', '', money(taskgroup['estimate_net']))
            items.row_style('FONTNAME', 0, -1, font.bold)
            items.row_style('ALIGNMENT', -1, -1, "RIGHT")
            items.row_style('SPAN', 1, 4)
            items.row_style('VALIGN', 0, -1, "BOTTOM")

            items.row('')

            if len(proposal['jobs']) == 1:
                totals.row(b('{} {} - {}'.format(_('Total'), taskgroup['code'], taskgroup['name']), font),
                    money(taskgroup['estimate_net']))
                taskgroup_subtotals_added = True

        if not taskgroup_subtotals_added:
            # taskgroup subtotals are added if there is only 1 job *and* it is itemized
            # in all other cases we're going to show the job total
            totals.row(b('{} {} - {}'.format(_('Total'), job['code'], job['name']), font), money(job['estimate'].net))

    totals.row_style('LINEBELOW', 0, 1, 0.25, colors.black)
    totals.row(_("Total without VAT"), money(proposal['estimate_total'].net))
    totals.row("19,00% "+_("VAT"), money(proposal['estimate_total'].tax))
    totals.row(_("Total including VAT"), money(proposal['estimate_total'].gross))

    return [
        items.get_table(ContinuationTable, repeatRows=1),
        totals.get_table()
    ]


def collate_lineitems(proposal, available_width, font):

    pages = []

    for job in proposal['jobs']:

        for taskgroup in job['taskgroups']:

            for task in taskgroup['tasks']:

                pages.append(PageBreak())

                t = TableFormatter([1, 0], available_width, font, debug=DEBUG_DOCUMENT)
                t.style.append(('LEFTPADDING', (0, 0), (-1, -1), 0))
                t.style.append(('RIGHTPADDING', (-1, 0), (-1, -1), 0))
                t.style.append(('VALIGN', (0, 0), (-1, -1), 'TOP'))

                t.row(b(job['code'], font), b(job['name'], font))
                t.row(b(taskgroup['code'], font), b(taskgroup['name'], font))
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

                for lineitem in task['lineitems']:
                    t.row(p(lineitem['name'], font),
                          ubrdecimal(lineitem['qty']),
                          p(lineitem['unit'], font),
                          money(lineitem['price']),
                          money(lineitem['price_per'])
                          )

                t.row_style('LINEBELOW', 0, -1, 0.25, colors.black)

                t.row('', ubrdecimal(task['qty']), b(task['unit'], font), '', money(task['estimate_net']))
                t.row_style('FONTNAME', 0, -1, font.bold)

                pages.append(t.get_table(ContinuationTable))

    return pages


def render(proposal, letterhead ):

    with BytesIO() as buffer:

        font = FontManager(letterhead.font)

        table_width, pagesize = calculate_table_width_and_pagesize(letterhead)

        proposal_date = date_format(date.today(), use_l10n=True)

        doc = NumberedSystoriDocument(buffer, pagesize=pagesize, debug=DEBUG_DOCUMENT)

        flowables = [

            heading_and_date('hallöööö', proposal_date, font,
                             table_width, debug=DEBUG_DOCUMENT),

            Spacer(0, 4*mm),

            Paragraph(force_break('HEADER'), font.normal),

            Spacer(0, 4*mm),

            KeepTogether(Paragraph(force_break('FOOTER'), font.normal)),

        ]

        doc.build(flowables, NumberedLetterheadCanvas.factory(letterhead), letterhead)

        return buffer.getvalue()
