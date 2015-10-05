from io import BytesIO
from datetime import date

from reportlab.lib.pagesizes import A6, A5, A4, A3, A2, A1, A0, LETTER, LEGAL, ELEVENSEVENTEEN, B6, B5, B4, B3, B2, B1,\
    B0, landscape
from reportlab.lib.units import mm, cm, inch
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph, Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas
from reportlab.lib import colors

from rlextra.pageCatcher.pageCatcher import storeFormsInMemory, restoreFormsInMemory, open_and_read

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
    def __init__(self, *args, stationary_filename="soft_briefbogen_2014.pdf", **kwargs):
        self.stationary_filename = stationary_filename
        super(LetterheadCanvas, self).__init__(*args, **kwargs)

def call_stationary(filename):
    return LetterheadCanvas(stationary_filename=filename)


class PortraitStationaryCanvas(StationaryCanvas, NumberedCanvas):
    stationary_filename = "soft_briefbogen_2014.pdf"


def render(letterhead):
    document_unit = DOCUMENT_UNIT.get(letterhead.document_unit)

    def systori_canvasmaker():
        return LetterheadCanvas

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


        doc.build(pages, canvasmaker=systori_canvasmaker)

        return buffer.getvalue()
