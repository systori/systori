from io import BytesIO
from datetime import date

from reportlab.lib.units import mm
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Spacer
from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from .style import NumberedLetterheadCanvas, NumberedSystoriDocument
from .style import force_break, heading_and_date
from .style import calculate_table_width_and_pagesize

from .font import FontManager


def render(letterhead):

    font = FontManager(letterhead.font)
    table_width, pagesize = calculate_table_width_and_pagesize(letterhead)

    invoice_date = date_format(date(*map(int, '2016-01-31'.split('-'))), use_l10n=True)

    with BytesIO() as buffer:

        flowables = []

        doc = NumberedSystoriDocument(buffer, pagesize=pagesize, debug=letterhead.debug)

        flowables.extend([
            Paragraph(force_break("""Musterfirma GmbH
            Herr Max Mustermann
            Musterstraße 123
            65321 Musterhausen
            """), font.normal),
            Spacer(0, 25*mm),

            heading_and_date(_("Invoice"), invoice_date, font, table_width, debug=letterhead.debug),
            Spacer(0, 4*mm),

            Paragraph(_("Invoice No.") + " 00000815", font.normal_right),
            Paragraph(_("Please indicate the correct invoice number on your payment."),
                      ParagraphStyle('', parent=font.small, alignment=TA_RIGHT)),
            Spacer(0, 10*mm),
            Paragraph(force_break('Dear Sir or Madam...'), font.normal),

            Spacer(0, 4*mm),
            Paragraph(force_break(lorem_100), font.normal),
            Paragraph(force_break(lorem_100*17), font.normal),
            ])

        doc.build(flowables, NumberedLetterheadCanvas.factory(letterhead), letterhead)

        return buffer.getvalue()

lorem_100 = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.<br></br>At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.<br></br>"
