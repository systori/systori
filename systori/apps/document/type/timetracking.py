from io import BytesIO
from datetime import date

from reportlab.lib.units import mm, cm
from reportlab.lib.utils import simpleSplit
from reportlab.platypus import Paragraph, Spacer, KeepTogether, PageBreak, Table, TableStyle
from reportlab.lib import colors

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.lib.templatetags.customformatting import ubrdecimal, money

import calendar

from .style import NumberedSystoriDocument, TableFormatter, ContinuationTable
from .style import chunk_text, force_break, p, b, br
from .style import NumberedLetterheadCanvas, NumberedCanvas
from .style import get_available_width_height_and_pagesize
from .style import heading_and_date, get_address_label, get_address_label_spacer
from .font import FontManager


DEBUG_DOCUMENT = True  # Shows boxes in rendered output


def collate_elements(data, month, year, available_width, available_height, font):

    cal = [[_('Mon'), _('Tue'), _('Wed'), _('Thu'), _('Fri'), _('Sat'), _('Sun')]]
    cal.extend(calendar.monthcalendar(year, month))

    pages = []

    table = Table(cal, available_width/7, available_height/6 - 4*mm)
    table.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.green)
    ]))
    pages.append(table)
    # for timer in data.all():
    #
    #     pages.append(Table([[b(_('Evidence Sheet'), font), "assad"]]))
    #
    #     pages.append(Table([
    #         [b(_('Project'), font), "asdasda"]
    #     ],
    #         colWidths=[30 * mm, None],
    #         style=[
    #             ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    #         ]
    #     ))
    #
    #     pages.append(Table([
    #         [b(_('Code'), font), "asdasd",
    #          br(_('Task'), font), "asdasdasd"],
    #         [b(_('P-Amount'), font), "asdasedsa"]
    #     ],
    #         colWidths=[30 * mm, 70 * mm, 30 * mm, None],
    #         style=TableStyle([
    #             ('SPAN', (3, 0), (-1, 0)),
    #         ])
    #     ))
    #
    #     pages.append(PageBreak())

    return pages


def render(data, letterhead, month, year):

    with BytesIO() as buffer:

        font = FontManager(letterhead.font)

        available_width, available_height, pagesize = get_available_width_height_and_pagesize(letterhead)

        proposal_date = date_format(date.today(), use_l10n=True)

        doc = NumberedSystoriDocument(buffer, pagesize=pagesize, debug=DEBUG_DOCUMENT)

        flowables = [

            heading_and_date(_('Monthly hours report for {}'.format(date_format(date(year, month, 1), "F Y", use_l10n=True))),
                             proposal_date, font, available_width, debug=DEBUG_DOCUMENT),

            Spacer(0, 4*mm),

        ] + collate_elements(data, month, year, available_width, available_height, font)

        doc.build(flowables, NumberedLetterheadCanvas.factory(letterhead), letterhead)

        return buffer.getvalue()
