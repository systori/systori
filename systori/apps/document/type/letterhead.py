from io import BytesIO
from datetime import date

from reportlab.lib.pagesizes import A6, A5, A4, A3, A2, A1, A0, LETTER, LEGAL, ELEVENSEVENTEEN, B6, B5, B4, B3, B2, B1,\
    B0, landscape
from reportlab.lib.units import mm, cm, inch
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph, Table, TableStyle, PageBreak
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.lib.templatetags.customformatting import ubrdecimal, money

from .style import LandscapeStationaryCanvas, StationaryCanvas, NumberedCanvas
from .style import p, b, br, nr

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
    def __init__(self, stationary_filename="soft_briefbogen_2014.pdf", *args, **kwargs):
        super(LetterheadCanvas, self).__init__(*args, **kwargs)
        self.stationary_filename = stationary_filename


def render(letterhead):
    document_unit = DOCUMENT_UNIT.get(letterhead.document_unit)

    with BytesIO() as buffer:

        pages = []

        pages.append(b(_('There are no billable Tasks available.')))

        doc = SimpleDocTemplate(buffer,
                pagesize = DOCUMENT_FORMAT[letterhead.document_format],
                topMargin = float(letterhead.top_margin)*document_unit,
                bottomMargin = float(letterhead.bottom_margin)*document_unit,
                leftMargin = float(letterhead.left_margin)*document_unit,
                rightMargin = float(letterhead.right_margin)*document_unit,
                showBoundary=True)

        canvas = LetterheadCanvas()

        doc.build(pages, canvasmaker=canvas)

        return buffer.getvalue()
