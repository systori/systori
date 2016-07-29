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


DEBUG_DOCUMENT = True  # Shows boxes in rendered output

def collate_elements(data, available_width, font):

    pages = []

    for entry in data.all():

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


def render(data, letterhead, month, year):

    with BytesIO() as buffer:

        font = FontManager(letterhead.font)

        table_width, pagesize = calculate_table_width_and_pagesize(letterhead)

        proposal_date = date_format(date.today(), use_l10n=True)

        doc = NumberedSystoriDocument(buffer, pagesize=pagesize, debug=DEBUG_DOCUMENT)

        flowables = [

            heading_and_date(_('Monthly working hours report for {}'.format(date_format(date(year, month, 1), "F Y", use_l10n=True))),
                             proposal_date, font, table_width, debug=DEBUG_DOCUMENT),

            Spacer(0, 4*mm),

        ] + collate_elements(data, table_width, font)

        doc.build(flowables, NumberedLetterheadCanvas.factory(letterhead), letterhead)

        return buffer.getvalue()
