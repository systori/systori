from . import font

from reportlab.lib.styles import StyleSheet1, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

stylesheet = StyleSheet1()

stylesheet.add(ParagraphStyle(name='Small',
                              fontName=font.normal,
                              fontSize=7,
                              leading=8.4)
               )

stylesheet.add(ParagraphStyle(name='Normal',
                              fontName=font.normal,
                              fontSize=10,
                              leading=12)
               )

stylesheet.add(ParagraphStyle(name='NormalRight',
                              parent=stylesheet['Normal'],
                              alignment=TA_RIGHT)
               )

stylesheet.add(ParagraphStyle(name='Bold',
                              fontName=font.bold,
                              fontSize=10,
                              leading=12)
               )

stylesheet.add(ParagraphStyle(name='BodyText',
                              parent=stylesheet['Normal'],
                              spaceBefore=6)
               )

stylesheet.add(ParagraphStyle(name='Italic',
                              parent=stylesheet['BodyText'],
                              fontName=font.italic)
               )

stylesheet.add(ParagraphStyle(name='Heading1',
                              parent=stylesheet['Normal'],
                              fontName=font.bold,
                              fontSize=18,
                              leading=22,
                              spaceAfter=6),
               alias='h1')

stylesheet.add(ParagraphStyle(name='Title',
                              parent=stylesheet['Normal'],
                              fontName=font.bold,
                              fontSize=18,
                              leading=22,
                              alignment=TA_CENTER,
                              spaceAfter=6),
               alias='title')

stylesheet.add(ParagraphStyle(name='Heading2',
                              parent=stylesheet['Normal'],
                              fontName=font.bold,
                              fontSize=14,
                              leading=18,
                              spaceBefore=12,
                              spaceAfter=6),
               alias='h2')

stylesheet.add(ParagraphStyle(name='Heading3',
                              parent=stylesheet['Normal'],
                              fontName=font.bold,
                              fontSize=12,
                              leading=14,
                              spaceBefore=12,
                              spaceAfter=6),
               alias='h3')

stylesheet.add(ParagraphStyle(name='Heading4',
                              parent=stylesheet['Normal'],
                              fontName=font.boldItalic,
                              fontSize=10,
                              leading=12,
                              spaceBefore=10,
                              spaceAfter=4),
               alias='h4')

stylesheet.add(ParagraphStyle(name='Heading5',
                              parent=stylesheet['Normal'],
                              fontName=font.bold,
                              fontSize=9,
                              leading=10.8,
                              spaceBefore=8,
                              spaceAfter=4),
               alias='h5')

stylesheet.add(ParagraphStyle(name='Heading6',
                              parent=stylesheet['Normal'],
                              fontName=font.bold,
                              fontSize=7,
                              leading=8.4,
                              spaceBefore=6,
                              spaceAfter=2),
               alias='h6')

stylesheet.add(ParagraphStyle(name='Bullet',
                              parent=stylesheet['Normal'],
                              firstLineIndent=0,
                              spaceBefore=3),
               alias='bu')

stylesheet.add(ParagraphStyle(name='Definition',
                              parent=stylesheet['Normal'],
                              firstLineIndent=0,
                              leftIndent=36,
                              bulletIndent=0,
                              spaceBefore=6,
                              bulletFontName=font.boldItalic),
               alias='df')


from django.utils.translation import ugettext as _
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm


def force_break(txt):
    return txt.replace('\n', '<br />')


def p(txt):
    return Paragraph(txt, stylesheet['Normal'])


def b(txt):
    return Paragraph(txt, stylesheet['Bold'])


def nr(txt):
    return Paragraph(str(txt), stylesheet['NormalRight'])


class NumberedCanvas(canvas.Canvas):

    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont(font.normal, 10)
        self.drawRightString(145*mm, 10*mm,
                             '{} {} {} {}'.format(_("Page"), self._pageNumber, _("of"), page_count))

