lorem_100 = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.<br></br>At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.<br></br>"


from io import BytesIO
from datetime import date

from reportlab.lib.pagesizes import A6, A5, A4, A3, A2, A1, A0, LETTER, LEGAL, ELEVENSEVENTEEN, B6, B5, B4, B3, B2, B1,\
    B0, landscape
from reportlab.lib.units import mm, cm, inch
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, KeepTogether, PageBreak
from reportlab.pdfgen import canvas
from reportlab.lib import colors

from rlextra.pageCatcher.pageCatcher import storeFormsInMemory, restoreFormsInMemory, open_and_read

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.lib.templatetags.customformatting import ubrdecimal, money

from .style import stylesheet, LandscapeStationaryCanvas, StationaryCanvas, NumberedCanvas, SystoriDocument
from .style import p, b, br, nr, force_break, heading_and_date

DOCUMENT_UNIT = {
    "mm": mm,
    "cm": cm,
    "inch": inch
}

DOCUMENT_FORMAT = {
    "A6" : A6,
    "A5" : A5,
    "A4" : A4,
    "A3" : A3,
    "A2" : A2,
    "A1" : A1,
    "A0" : A0,
    "LETTER" : LETTER,
    "LEGAL" : LEGAL,
    "ELEVENSEVENTEEN" : ELEVENSEVENTEEN,
    "B6" : B6,
    "B5" : B5,
    "B4" : B4,
    "B3" : B3,
    "B2" : B2,
    "B1" : B1,
    "B0" : B0,
}


class LetterheadCanvas(StationaryCanvas, NumberedCanvas):
    def __init__(self, letterhead_pdf, *args, **kwargs):
        self.stationary_pages = letterhead_pdf
        super(LetterheadCanvas, self).__init__(*args, **kwargs)


def render(letterhead):
    document_unit = DOCUMENT_UNIT.get(letterhead.document_unit)
    invoice_date = date_format(date(*map(int, '2016-01-31'.split('-'))), use_l10n=True)

    def canvas_maker(*args, **kwargs):
        return LetterheadCanvas(letterhead.letterhead_pdf, *args, **kwargs)

    with BytesIO() as buffer:

        pages = []

        doc = SystoriDocument(buffer,
            pagesize = DOCUMENT_FORMAT[letterhead.document_format],
            debug=letterhead.debug)

        frame1 = {
            'top_padding' : float(letterhead.top_margin_page1)*document_unit,
            'bottom_padding' : float(letterhead.bottom_margin_page1)*document_unit,
            'left_padding' : float(letterhead.left_margin_page1)*document_unit,
            'right_padding' : float(letterhead.right_margin_page1)*document_unit,
        }
        frame2 = {
            'top_padding' : float(letterhead.top_margin_page2)*document_unit,
            'bottom_padding' : float(letterhead.bottom_margin_page2)*document_unit,
            'left_padding' : float(letterhead.left_margin_page2)*document_unit,
            'right_padding' : float(letterhead.right_margin_page2)*document_unit,
        }

        pages.extend([
            Paragraph(force_break("""Musterfirma GmbH
            Herr Max Mustermann
            Musterstraße 123
            65321 Musterhausen
            """), stylesheet['Normal']),
            Spacer(0, 22*mm),

            heading_and_date(_("Invoice"),invoice_date, doc.width, debug=letterhead.debug),
            Spacer(0, 4*mm),

            Paragraph(_("Invoice No.")+" 00000815", stylesheet['NormalRight']),
            Paragraph(_("Please indicate the correct invoice number on your payment."),
                      ParagraphStyle('', parent=stylesheet['Small'], alignment=TA_RIGHT)),
            Spacer(0, 1*mm),
            Paragraph(force_break('Dear Sir or Madam...'), stylesheet['Normal']),

            Spacer(0, 4*mm),
            Paragraph(force_break(lorem_100), stylesheet['Normal']),
            Paragraph(force_break(lorem_100*17), stylesheet['Normal']),
            ])

        doc.build(pages, frame1=frame1, frame2=frame2, canvasmaker=canvas_maker)

        return buffer.getvalue()
