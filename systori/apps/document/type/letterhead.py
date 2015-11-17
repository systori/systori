lorem_100 = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.<br></br>At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.<br></br>"

from io import BytesIO
from datetime import date

from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Spacer
from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from .style import stylesheet, LetterheadCanvas, SystoriDocument
from .style import force_break, heading_and_date
from .style import DOCUMENT_FORMAT, DOCUMENT_UNIT


def render(letterhead):
    document_unit = DOCUMENT_UNIT[letterhead.document_unit]
    if letterhead.orientation == 'landscape':
        pagesize = landscape(DOCUMENT_FORMAT[letterhead.document_format])
    else:
        pagesize = DOCUMENT_FORMAT[letterhead.document_format]
    page_width = pagesize[0]
    table_width = page_width - float(letterhead.right_margin)*document_unit\
                             - float(letterhead.left_margin)*document_unit

    invoice_date = date_format(date(*map(int, '2016-01-31'.split('-'))), use_l10n=True)

    def canvas_maker(*args, **kwargs):
        return LetterheadCanvas(letterhead.letterhead_pdf, *args, **kwargs)

    with BytesIO() as buffer:

        flowables = []

        doc = SystoriDocument(buffer, pagesize=pagesize, debug=letterhead.debug)

        flowables.extend([
            Paragraph(force_break("""Musterfirma GmbH
            Herr Max Mustermann
            Musterstraße 123
            65321 Musterhausen
            """), stylesheet['Normal']),
            Spacer(0, 25*mm),

            heading_and_date(_("Invoice"), invoice_date, table_width, debug=letterhead.debug),
            Spacer(0, 4*mm),

            Paragraph(_("Invoice No.")+" 00000815", stylesheet['NormalRight']),
            Paragraph(_("Please indicate the correct invoice number on your payment."),
                      ParagraphStyle('', parent=stylesheet['Small'], alignment=TA_RIGHT)),
            Spacer(0, 10*mm),
            Paragraph(force_break('Dear Sir or Madam...'), stylesheet['Normal']),

            Spacer(0, 4*mm),
            Paragraph(force_break(lorem_100), stylesheet['Normal']),
            Paragraph(force_break(lorem_100*17), stylesheet['Normal']),
            ])

        doc.build(flowables, canvasmaker=canvas_maker, letterhead=letterhead)

        return buffer.getvalue()