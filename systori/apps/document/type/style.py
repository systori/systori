from .font import fonts

import os.path
from django.conf import settings
from django.utils.translation import ugettext as _

from rlextra.pageCatcher.pageCatcher import storeFormsInMemory, restoreFormsInMemory, open_and_read

from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import BaseDocTemplate, PageTemplate
from reportlab.platypus import Frame, Paragraph, Table, Spacer
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors, pagesizes, units


def _simpleSplit(txt,mW,SW):
    L = []
    ws = SW(' ')
    O = []
    w = -ws
    for t in txt.split():
        lt = SW(t)
        if w+ws+lt<=mW or O==[]:
            O.append(t)
            w = w + ws + lt
        else:
            L.append(' '.join(O))
            O = [t]
            w = lt
    if O!=[]: L.append(' '.join(O))
    return L

# from reportlab.lib.utils import simpleSplit
def simpleSplit(text,fontName,fontSize,maxWidth):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    lines = text.replace('<br />','\n').split('\n')
    SW = lambda text, fN=fontName, fS=fontSize: stringWidth(text, fN, fS)
    if maxWidth:
        L = []
        for l in lines:
            L.extend(_simpleSplit(l,maxWidth,SW))
        lines = L
    return lines


def get_available_width_height_and_pagesize(letterhead):
    document_unit = getattr(units, letterhead.document_unit)
    pagesize = getattr(pagesizes, letterhead.document_format)
    if letterhead.orientation == 'landscape':
        pagesize = pagesizes.landscape(pagesize)
    width_margin = letterhead.left_margin + letterhead.right_margin
    height_margin = letterhead.top_margin + letterhead.bottom_margin
    return pagesize[0] - float(width_margin) * document_unit,\
           pagesize[1] - float(height_margin) * document_unit,\
           pagesize


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


def p(txt, font):
    return Paragraph(txt, font.normal)


def b(txt, font):
    return Paragraph(txt, font.bold)


def br(txt, font):
    return Paragraph(str(txt), font.bold_right)


def nr(txt, font):
    return Paragraph(str(txt), font.normal_right)


def heading_and_date(heading, date, font, available_width, debug=False):

    t = TableFormatter([0, 1], available_width, font, debug=debug)
    t.style.append(('GRID', (0, 0), (-1, -1), 1, colors.transparent))
    t.row(Paragraph(heading, font.h2), Paragraph(date, font.normal_right))
    t.style.append(('ALIGNMENT', (0, 0), (-1, -1), "RIGHT"))
    t.style.append(('RIGHTPADDING', (0, 0), (-1, -1), 0))

    return t.get_table(Table)


class StationaryCanvas(canvas.Canvas):

    stationary_pages = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cover_pdf = os.path.join(settings.MEDIA_ROOT, self.stationary_pages.name)
        cover_pdf = open_and_read(cover_pdf)
        self.page_info_page1, self.page_content = storeFormsInMemory(cover_pdf, all=True)
        restoreFormsInMemory(self.page_content, self)

    def showPage(self):
        if self._pageNumber > 1 and len(self.page_info_page1) > 1:
            self.doForm(self.page_info_page1[1])
        else:
            self.doForm(self.page_info_page1[0])
        super().showPage()


class NumberedCanvas(canvas.Canvas):

    def __init__(self, *args, page_number_x, page_number_y, page_number_y_next, font, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.page_number_x = page_number_x
        self.page_number_y = page_number_y
        self.page_number_y_next = page_number_y_next
        self.font = font

    def showPage(self):
        """ Instead of 'showing' the page we save the render state for later. """
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """ Now that we know how many pages there are we can render all of them. """
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.setFont('{}-Regular'.format(self.font), 10)
        if self._pageNumber == 1:
            self.drawRightString(self.page_number_x, self.page_number_y - 20,
                                 _("Page {} of {}").format(self._pageNumber, page_count))
        else:
            self.drawRightString(self.page_number_x, self.page_number_y_next - 20,
                                 _("Page {} of {}").format(self._pageNumber, page_count))


class LetterheadCanvas(StationaryCanvas):

    def __init__(self, letterhead_pdf, *args, **kwargs):
        self.stationary_pages = letterhead_pdf
        super().__init__(*args, **kwargs)

    @staticmethod
    def factory(letterhead):
        return lambda *args, **kwargs: LetterheadCanvas(letterhead.letterhead_pdf, *args, **kwargs)


class NumberedLetterheadCanvas(StationaryCanvas, NumberedCanvas):

    def __init__(self, letterhead_pdf, *args, **kwargs):
        self.stationary_pages = letterhead_pdf
        super().__init__(*args, **kwargs)

    @staticmethod
    def factory(letterhead):
        return lambda *args, **kwargs: NumberedLetterheadCanvas(letterhead.letterhead_pdf, *args, **kwargs)


class NumberedLetterheadCanvasWithoutFirstPage(StationaryCanvas, NumberedCanvas):

    def __init__(self, letterhead_pdf, *args, **kwargs):
        self.stationary_pages = letterhead_pdf
        super().__init__(*args, **kwargs)

    @staticmethod
    def factory(letterhead):
        return lambda *args, **kwargs: NumberedLetterheadCanvasWithoutFirstPage(letterhead.letterhead_pdf,
                                                                                *args, **kwargs)


class SystoriDocument(BaseDocTemplate):

    def __init__(self, buffer, pagesize, debug=False):
        super().__init__(buffer,
                         pagesize=pagesize,
                         topMargin=0,
                         bottomMargin=0,
                         leftMargin=0,
                         rightMargin=0,
                         showBoundary=debug)

    def onFirstPage(self, canvas, document):
        pass

    def onLaterPages(self, canvas, document):
        pass

    def handle_pageBegin(self):
        self._handle_pageBegin()
        self._handle_nextPageTemplate('Later')

    def build(self, flowables, canvasmaker=NumberedCanvas, letterhead=None):
        self._calc()

        if letterhead:
            document_unit = getattr(units, letterhead.document_unit)
            frame_x = float(letterhead.left_margin) * document_unit
            frame_y = float(letterhead.bottom_margin) * document_unit
            frame_width = self.width - float(letterhead.left_margin+letterhead.right_margin) * document_unit
            frame_height_first = self.height-float(letterhead.top_margin+letterhead.bottom_margin)*document_unit
            frame_height_later = self.height-float(letterhead.top_margin_next+letterhead.bottom_margin)*document_unit
            padding = dict.fromkeys(['leftPadding', 'bottomPadding', 'rightPadding', 'topPadding'], 0)
        else:
            frame_x = 25
            frame_y = 25
            frame_width = self.width - 50
            frame_height_first = frame_height_later = self.height - 50
            padding = dict.fromkeys(['leftPadding', 'bottomPadding', 'rightPadding', 'topPadding'], 6)

        # Frame(x, y, width, height, padding...)
        frame_first = Frame(frame_x, frame_y, frame_width, frame_height_first, **padding)
        frame_later = Frame(frame_x, frame_y, frame_width, frame_height_later, **padding)

        self.addPageTemplates([
            PageTemplate(id='First', frames=frame_first, onPage=self.onFirstPage, pagesize=self.pagesize,
                         autoNextPageTemplate=True),
            PageTemplate(id='Later', frames=frame_later, onPage=self.onLaterPages, pagesize=self.pagesize)
        ])

        super().build(flowables, canvasmaker=canvasmaker)


class NumberedSystoriDocument(BaseDocTemplate):

    def __init__(self, buffer, pagesize, debug=False):
        super().__init__(buffer,
                         pagesize=pagesize,
                         topMargin=0,
                         bottomMargin=0,
                         leftMargin=0,
                         rightMargin=0,
                         showBoundary=debug)

    def onFirstPage(self, canvas, document):
        pass

    def onLaterPages(self, canvas, document):
        pass

    def handle_pageBegin(self):
        self._handle_pageBegin()
        self._handle_nextPageTemplate('Later')

    def build(self, flowables, canvasmaker=NumberedCanvas, letterhead=None):
        self._calc()

        if letterhead:
            document_unit = getattr(units, letterhead.document_unit)
            frame_x = float(letterhead.left_margin) * document_unit
            frame_y = float(letterhead.bottom_margin) * document_unit
            frame_y_next = float(letterhead.bottom_margin_next) * document_unit
            frame_width = self.width - float(letterhead.left_margin+letterhead.right_margin) * document_unit
            frame_height_first = self.height-float(letterhead.top_margin+letterhead.bottom_margin)*document_unit
            frame_height_later = self.height-float(letterhead.top_margin_next+letterhead.bottom_margin_next)*document_unit
            padding = dict.fromkeys(['leftPadding', 'bottomPadding', 'rightPadding', 'topPadding'], 0)
        else:
            frame_x = 25
            frame_y = 25
            frame_y_next = 25
            frame_width = self.width - 50
            frame_height_first = frame_height_later = self.height - 50
            padding = dict.fromkeys(['leftPadding', 'bottomPadding', 'rightPadding', 'topPadding'], 6)

        # Frame(x, y, width, height, padding...)
        frame_first = Frame(frame_x, frame_y, frame_width, frame_height_first, **padding)
        frame_later = Frame(frame_x, frame_y_next, frame_width, frame_height_later, **padding)

        self.addPageTemplates([
            PageTemplate(id='First', frames=frame_first, onPage=self.onFirstPage, pagesize=self.pagesize, autoNextPageTemplate=True),
            PageTemplate(id='Later', frames=frame_later, onPage=self.onLaterPages, pagesize=self.pagesize)
        ])

        def page_number_canvas_maker(*args, **kwargs):
            # Hand over Margins to NumberedCanvas
            kwargs['page_number_x'] = frame_x + frame_width
            kwargs['page_number_y'] = frame_y
            kwargs['page_number_y_next'] = frame_y_next
            kwargs['font'] = letterhead.font
            return canvasmaker(*args, **kwargs)

        super().build(flowables, canvasmaker=page_number_canvas_maker)


class ContinuationTable(Table):

    def draw(self):

        self.canv.saveState()
        self.canv.setFont('{}-Italic'.format(self.canv.font), 10)

        if getattr(self, '_splitCount', 0) > 1:
            # if uncommented write ...Continuation line above next table segment
            # self.canv.drawString(0, self._height + 5*mm, '... '+_('Continuation'))
            pass

        if getattr(self, '_splitCount', 0) >= 1 and not hasattr(self, '_lastTable'):
            # self.canv.drawRightString(self._width, -7*mm, _('Continuation')+' ...')
            self.canv.drawString(0, -20, _('Continuation')+' ...')

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


class TableStyler:
    font_size = 10

    def __init__(self, font, base_style=True, debug=False):
        self.font = font.normal
        self.lines = []
        self.style = []
        if base_style:
            self.style += [
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('FONTNAME', (0, 0), (-1, -1), self.font.fontName),
                ('FONTSIZE', (0, 0), (-1, -1), self.font_size)
            ]
        if debug:
            self.style += [
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black)
            ]

    def get_table(self, table_class=Table, **kwargs):
        return table_class(self.lines, style=self.style, **kwargs)

    def row(self, *line):
        self.lines.append(line)

    @property
    def _row_num(self):
        return len(self.lines)-1

    def row_style(self, name, from_column, to_column, *args):
        args = tuple(arg.fontName if isinstance(arg, ParagraphStyle) else arg for arg in args)
        self.style.append((name, (from_column, self._row_num), (to_column, self._row_num))+args)

    def keep_previous_n_rows_together(self, n):
        self.style.append(('NOSPLIT', (0, self._row_num-n+1), (0, self._row_num)))

    def keep_next_n_rows_together(self, n):
        self.style.append(('NOSPLIT', (0, self._row_num+n-1), (0, self._row_num)))


class TableFormatter(TableStyler):

    def __init__(self, columns, width, font, pad=5*mm, trim_ends=True, debug=False):
        super().__init__(font, debug)
        assert columns.count(0) == 1, "Must have exactly one stretch column."
        self._maximums = columns.copy()
        self._available_width = width
        self._pad = pad
        self._trim_ends = trim_ends
        self.columns = columns

    def get_table(self, table_class=Table, **kwargs):
        return table_class(self.lines, colWidths=self.get_widths(), style=self.style, **kwargs)

    def row(self, *line):
        for i, column in enumerate(self.columns):
            if column != 0 and i < len(line):
                self._maximums[i] = max(self._maximums[i], self.string_width(line[i]))
        self.lines.append(line)

    def string_width(self, txt):
        if isinstance(txt, str):
            return stringWidth(txt, self.font.fontName, self.font_size)
        else:
            return stringWidth(txt.text, self.font.fontName, self.font_size)

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


def get_address_label(document, font):
    if document.get('business') is '':
        return Paragraph(force_break(document.get('address_label', None) or """\
        {salutation} {first_name} {last_name}
        {address}
        {postal_code} {city}
        """.format(**document)), font.normal)
    else:
        return Paragraph(force_break(document.get('address_label', None) or """\
        {business}
        {salutation} {first_name} {last_name}
        {address}
        {postal_code} {city}
        """.format(**document)), font.normal)


def get_address_label_spacer(document):
    if document.get('business') is '':
        return Spacer(0, 30*mm)
    else:
        return Spacer(0, 26*mm)
