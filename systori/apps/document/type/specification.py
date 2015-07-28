from io import BytesIO
from datetime import date

from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer, KeepTogether, PageBreak
from reportlab.lib import colors

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.lib.templatetags.customformatting import ubrdecimal, money

from .style import SystoriDocument, TableFormatter, ContinuationTable
from .style import stylesheet, chunk_text, force_break, p, b
from .style import PortraitStationaryCanvas
from . import font


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

                for chunk in chunk_text(task['description']):
                    t.row('', p(chunk))
                    t.row_style('SPAN', 1, -2)

                task_total_column = money(task['total'])
                if task['is_optional']:
                    task_total_column = _('Optional')
                elif not task['selected']:
                    task_total_column = _('Alternative')

                t.row('', '', ubrdecimal(task['qty']), p(task['unit']), '..........', '..........')
                t.row_style('ALIGNMENT', 1, -1, "RIGHT")

                t.row_style('BOTTOMPADDING', 0, -1, 10)

            t.row('', b('{} {} - {}'.format(_('Total'), taskgroup['code'], taskgroup['name'])),
                  '', '', '', '..........')
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
                  '....................')
    t.row_style('LINEBELOW', 0, 1, 0.25, colors.black)

    t.row(_("Total without VAT"), '....................')
    t.row("19,00% "+_("VAT"), '....................')
    t.row(_("Total including VAT"), '....................')

    return t.get_table()


def render(proposal, format):

    with BytesIO() as buffer:

        proposal_date = date_format(date(*map(int, proposal['date'].split('-'))), use_l10n=True)

        doc = SystoriDocument(buffer, debug=DEBUG_DOCUMENT)

        flowables = [

            Paragraph(force_break("""\
            {business}
            z.H. {salutation} {first_name} {last_name}
            {address}
            {postal_code} {city}
            """.format(**proposal)), stylesheet['Normal']),

            Spacer(0, 18*mm),

            Paragraph(proposal_date, stylesheet['NormalRight']),

            Spacer(0, 4*mm),

            Paragraph(force_break(proposal['header']), stylesheet['Normal']),

            Spacer(0, 4*mm),

            collate_tasks(proposal, doc.width),

            collate_tasks_total(proposal, doc.width),

            Spacer(0, 10*mm),

            KeepTogether(Paragraph(force_break(proposal['footer']), stylesheet['Normal'])),

            ]

        if format == 'print':
            doc.build(flowables)
        else:
            doc.build(flowables, canvasmaker=PortraitStationaryCanvas)

        return buffer.getvalue()

