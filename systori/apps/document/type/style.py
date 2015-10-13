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

stylesheet.add(ParagraphStyle(name='BoldRight',
                              parent=stylesheet['Bold'],
                              alignment=TA_RIGHT)
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


import os.path
from django.conf import settings
from django.utils.translation import ugettext as _

from rlextra.pageCatcher.pageCatcher import storeFormsInMemory, restoreFormsInMemory, open_and_read

from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.pagesizes import A4

from reportlab.platypus import BaseDocTemplate, PageTemplate
from reportlab.platypus import Frame, Paragraph, Table
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, cm
from reportlab.lib import colors


def chunk_text(txt, max_length=1500):
    """ Break the txt down into paragraphs. Each chunk is guaranteed to
        be less than max_length (so that it will fit on a page).
        This is necessary for Table cells since ReportLab cannot
        split cells across pages. Instead we add a table row for each chunk.
    """
    if not isinstance(txt, list):
        txt = txt.split('<br />')

    if txt:

        if len(txt[0]) < max_length:
            yield txt[0]

        else:
            yield txt[0][:max_length]
            txt.insert(1, txt[0][max_length:])

        yield from chunk_text(txt[1:])


def force_break(txt):
    return txt.replace('\n', '<br />')


def p(txt):
    return Paragraph(txt, stylesheet['Normal'])


def b(txt):
    return Paragraph(txt, stylesheet['Bold'])

def br(txt):
    return Paragraph(str(txt), stylesheet['BoldRight'])

def nr(txt):
    return Paragraph(str(txt), stylesheet['NormalRight'])

def heading_and_date(heading, date, available_width, debug=False):

    t = TableFormatter([0, 1], available_width, debug=debug)
    t.style.append(('GRID', (0, 0), (-1, -1), 1, colors.transparent))
    t.row(Paragraph(heading, stylesheet['h2']), Paragraph(date, stylesheet['NormalRight']))
    t.style.append(('ALIGNMENT', (0, 0), (-1, -1), "RIGHT"))
    t.style.append(('RIGHTPADDING', (0,0), (-1,-1), 0))

    return t.get_table(Table)


class StationaryCanvas(canvas.Canvas):

    stationary_pages = None

    def __init__(self, *args, **kwargs):
        super(StationaryCanvas, self).__init__(*args, **kwargs)
        cover_pdf = os.path.join(settings.MEDIA_ROOT, self.stationary_pages.name)
        cover_pdf = open_and_read(cover_pdf)

        self.page_info_page1, self.page_content = storeFormsInMemory(cover_pdf, all=True)
        restoreFormsInMemory(self.page_content, self)

    def showPage(self):
        if self._pageNumber > 1 and len(self.page_info_page1) > 1:
            self.doForm(self.page_info_page1[1])
        else:
            self.doForm(self.page_info_page1[0])
        super(StationaryCanvas, self).showPage()


class StationaryCanvasWithoutFirstPage(StationaryCanvas):

    def showPage(self):
        self.doForm(self.page_info[1])
        super(StationaryCanvas, self).showPage()


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
        self.drawRightString(149*mm, 10*mm,
                             '{} {} {} {}'.format(_("Page"), self._pageNumber, _("of"), page_count))


class PortraitStationaryCanvas(StationaryCanvas, NumberedCanvas):
    stationary_filename = "soft_briefbogen_2014.pdf"


class PortraitStationaryCanvasWithoutFirstPage(StationaryCanvasWithoutFirstPage, NumberedCanvas):
    stationary_filename = "soft_briefbogen_2014.pdf"


class LandscapeStationaryCanvas(StationaryCanvas):
    stationary_filename = "softronic2_landscape.pdf"


class SystoriDocument(BaseDocTemplate):

    def __init__(self, buffer, pagesize, debug=False):
        super(SystoriDocument, self).__init__(buffer,
                                              pagesize=pagesize,
                                              topMargin=0,
                                              bottomMargin=0,
                                              leftMargin=0,
                                              rightMargin=0,
                                              showBoundary=debug
                                              )

    def onFirstPage(self, canvas, document):
        pass

    def onLaterPages(self, canvas, document):
        pass

    def handle_pageBegin(self):
        self._handle_pageBegin()
        self._handle_nextPageTemplate('Later')

    def build(self, flowables, frame1=None, frame2=None,  canvasmaker=NumberedCanvas):
        self._calc()
        frame1 = Frame(self.leftMargin, self.bottomMargin,
                      self.width, self.height,
                      leftPadding=frame1['left_padding'], bottomPadding=frame1['right_padding'],
                      rightPadding=frame1['right_padding'], topPadding=frame1['top_padding'])
        frame2 = Frame(self.leftMargin, self.bottomMargin,
                      self.width, self.height,
                      leftPadding=frame2['left_padding'], bottomPadding=frame2['right_padding'],
                      rightPadding=frame2['right_padding'], topPadding=frame2['top_padding'])
        self.addPageTemplates([
            PageTemplate(id='First', frames=frame1, onPage=self.onFirstPage, pagesize=self.pagesize),
            PageTemplate(id='Later', frames=frame2, onPage=self.onLaterPages, pagesize=self.pagesize)
        ])
        super(SystoriDocument, self).build(flowables, canvasmaker=canvasmaker)


class ContinuationTable(Table):

    def draw(self):

        self.canv.saveState()
        self.canv.setFont(font.italic, 10)

        if getattr(self, '_splitCount', 0) > 1:
            self.canv.drawString(0, self._height + 5*mm, '... '+_('Continuation'))

        if getattr(self, '_splitCount', 0) >= 1 and not hasattr(self, '_lastTable'):
            self.canv.drawRightString(self._width, -7*mm, _('Continuation')+' ...')

        self.canv.restoreState()

        super(ContinuationTable, self).draw()

    def onSplit(self, table, byRow=1):
        """ Figure out the number of the split in the table and whether
            this split is the last one to occur. This is used to then
            intelligently display 'continued...' header/footers.
        """
        if not hasattr(self, '_splitCount'):
            self._splitCount = 0

        if not hasattr(self, '_splitR0'):
            self._splitR0 = table
            table._splitCount = self._splitCount+1
        else:
            table._splitCount = self._splitR0._splitCount+1
            table._lastTable = True


class TableFormatter:

    font = font.normal
    font_size = 10

    def __init__(self, columns, width, pad=5*mm, trim_ends=True, debug=False):
        assert columns.count(0) == 1, "Must have exactly one stretch column."
        self._maximums = columns.copy()
        self._available_width = width
        self._pad = pad
        self._trim_ends = trim_ends
        self.columns = columns
        self.lines = []
        self.style = [
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('FONTNAME', (0, 0), (-1, -1), self.font),
            ('FONTSIZE', (0, 0), (-1, -1), self.font_size)
        ]
        if debug:
            self.style += [
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black)
            ]

    def get_table(self, table_class=Table, **kwargs):
        return table_class(self.lines, colWidths=self.get_widths(), style=self.style, **kwargs)

    def row(self, *line):
        for i, column in enumerate(self.columns):
            if column != 0 and i < len(line):
                self._maximums[i] = max(self._maximums[i], self.string_width(line[i]))
        self.lines.append(line)

    def string_width(self, txt):
        if isinstance(txt, str):
            return stringWidth(txt, self.font, self.font_size)
        else:
            return stringWidth(txt.text, self.font, self.font_size)

    def get_widths(self):

        widths = self._maximums.copy()

        for i, w in enumerate(widths):
            if w != 0:
                widths[i] += self._pad

        if self._trim_ends:
            trim = self._pad/2
            widths[0] -= trim if widths[0] >= trim else 0
            widths[-1] -= trim if widths[-1] >= trim else 0

        widths[widths.index(0)] = self._available_width - sum(widths)

        return widths

    @property
    def _row_num(self):
        return len(self.lines)-1

    def row_style(self, name, from_column, to_column, *args):
        self.style.append((name, (from_column, self._row_num), (to_column, self._row_num))+args)

    def keep_previous_n_rows_together(self, n):
        self.style.append(('NOSPLIT', (0, self._row_num-n+1), (0, self._row_num)))

