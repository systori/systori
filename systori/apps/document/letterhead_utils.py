from PyPDF2 import PdfFileReader
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from reportlab.lib.units import cm, inch

from .models import Letterhead


def clean_letterhead_pdf(file, save=False):
    """
    this method expects a File and tries to determine some metadata - at the moment it's supporting PDF only.
    page size = MediaBox regarding http://partners.adobe.com/public/developer/en/pdf/PDFReference.pdf page 88

    available Formats unit = Points
    :param file: file object from upload form
    :return: letterhead_user_specification dictionary to instantiate a Letterhead Object
    """
    _W, _H = (595, 842)
    # 21cm 595.275590551181pt 29.7cm 841.8897637795275pt
    _BW, _BH = (709, 1001)
    # 25cm 708.6614173228346pt 35.3cm 1000.6299212598424pt
    available_formats = {
        (_W*0.5, _H*0.5): "A6",
        (_W*0.5, _H): "A5",
        (_W, _H): "A4",
        (_W*2, _H): "A3",
        (_W*2, _H*2): "A2",
        (_W*4, _H*2): "A1",
        (_W*4, _H*4): "A0",
        (612, 792): "LETTER",
        (612, 1008): "LEGAL",
        (792, 1224): "ELEVENSEVENTEEN",
        # 8.5inch 612pt 11inch 792pt 14inch 1008pt 17inch 1224pt
        (_BW*.5, _BH*.5): 'B6',
        (_BH*.5, _BW): 'B5',
        (_BW, _BH): 'B4',
        (_BH*2, _BW): 'B3',
        (_BW*2, _BH*2): 'B2',
        (_BH*4, _BW*2): 'B1',
        (_BW*4, _BH*4): 'B0'
    }

    page = PdfFileReader(file).getPage(0)

    rounded_width = round(page.mediaBox.getWidth())
    rounded_height = round(page.mediaBox.getHeight())

    letterhead_user_specification = {}
    # defaults
    letterhead_user_specification['letterhead_pdf'] = file
    letterhead_user_specification['top_margin_page1'] = 25
    letterhead_user_specification['right_margin_page1'] = 25
    letterhead_user_specification['bottom_margin_page1'] = 25
    letterhead_user_specification['left_margin_page1'] = 25
    letterhead_user_specification['top_margin_page2'] = 25
    letterhead_user_specification['right_margin_page2'] = 25
    letterhead_user_specification['bottom_margin_page2'] = 25
    letterhead_user_specification['left_margin_page2'] = 25
    letterhead_user_specification['top_margin_pageN'] = 25
    letterhead_user_specification['right_margin_pageN'] = 25
    letterhead_user_specification['bottom_margin_pageN'] = 25
    letterhead_user_specification['left_margin_pageN'] = 25
    letterhead_user_specification['top_margin_pageZ'] = 25
    letterhead_user_specification['right_margin_pageZ'] = 25
    letterhead_user_specification['bottom_margin_pageZ'] = 25
    letterhead_user_specification['left_margin_pageZ'] = 25
    letterhead_user_specification['document_unit'] = 'mm'


    if (rounded_width, rounded_height) in available_formats:
        letterhead_user_specification['document_format'] = available_formats[(rounded_width, rounded_height)]
        letterhead_user_specification['orientation'] = 'portrait'
    elif (rounded_height, rounded_width) in available_formats:
        letterhead_user_specification['document_format'] = available_formats[(rounded_height, rounded_width)]
        letterhead_user_specification['orientation'] = 'landscape'
    else:
        raise ValidationError(_('The uploaded file format is not supported.'), code='invalid')

    if save:
        letterhead = Letterhead.objects.create(**letterhead_user_specification)
        letterhead.name = _("Letterhead {}").format(letterhead.id)
        letterhead.save()
        return letterhead

    return True
