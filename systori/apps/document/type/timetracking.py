from io import BytesIO
from decimal import Decimal
from datetime import date
from collections import OrderedDict

from reportlab.lib.units import mm, cm
from reportlab.lib.utils import simpleSplit
from reportlab.platypus import Paragraph, Spacer, KeepTogether, PageBreak, Table, TableStyle
from reportlab.lib import colors

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.lib.templatetags.customformatting import ubrdecimal, money
from systori.apps.timetracking.models import Timer
from systori.apps.timetracking.utils import format_seconds

import calendar

from .style import NumberedSystoriDocument, TableStyler
from .style import chunk_text, force_break, p, b, br
from .style import NumberedLetterheadCanvas, NumberedCanvas
from .style import get_available_width_height_and_pagesize
from .style import heading_and_date, get_address_label, get_address_label_spacer
from .font import FontManager


DEBUG_DOCUMENT = False  # Shows boxes in rendered output


def seconds_to_hours(seconds):
    return Decimal(round(seconds / 60.0 / 60.0, 1))


class TimeSheet:

    WEEKDAYS = [_('Mon'), _('Tue'), _('Wed'), _('Thu'), _('Fri'), _('Sat'), _('Sun')]

    CATEGORIES = [p[0] for p in Timer.KIND_CHOICES if p[0] != Timer.WORK]

    def __init__(self, user, year, month):
        self.user = user
        self.names = []
        self.numbers = []
        self.mondays = []
        start, self.days = calendar.monthrange(year, month)
        for day in range(31):
            if day < self.days:
                self.names.append(self.WEEKDAYS[(day+start) % 7])
                if ((day+start) % 7) == 0:
                    self.mondays.append(day)
                self.numbers.append(str(day+1))
            else:
                self.names.append("")
                self.numbers.append("")
        self.names.append(_("Total"))
        self.names.append(_("Project"))
        self.projects = OrderedDict()
        self.special = OrderedDict([(c, [Decimal(0)]*self.days) for c in self.CATEGORIES])
        self.totals = [Decimal(0)]*self.days
        self.overhead = [Decimal(0)]*self.days

    def add(self, timer):
        day_idx = timer.date.day-1
        hours = seconds_to_hours(timer.duration)
        category = timer.kind
        slot = None
        if category == Timer.WORK:
            slot = self.projects.setdefault(_("Uncategorized"), [Decimal(0)]*self.days)
        elif category in self.special:
            slot = self.special[category]
        slot[day_idx] += hours
        self.totals[day_idx] += hours

    def get_table(self, available_width, font):
        ts = TableStyler(font, base_style=False)
        ts.style.append(('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black))
        ts.style.append(('LINEAFTER', (30, 0), (30, -1), 1.5, colors.black))
        ts.style.append(('BOX', (0, 0), (-1, -1), 0.25, colors.black))
        ts.style.append(('FONTSIZE', (0, 0), (-2, 1), 9))
        ts.style.append(('LEFTPADDING', (0, 0), (-2, -1), 2))
        ts.style.append(('RIGHTPADDING', (0, 0), (-2, -1), 2))
        ts.style.append(('ALIGNMENT', (0, 2), (-2, -1), "RIGHT"))

        for monday in self.mondays:
            ts.style.append(('LINEBEFORE', (monday, 0), (monday, -1), 1.5, colors.black))

        ts.row(*self.numbers)
        ts.row_style('ALIGNMENT', 0, -1, "CENTER")

        ts.row(*self.names)
        ts.row_style('ALIGNMENT', 0, -1, "CENTER")
        ts.row_style('LINEBELOW', 0, -1, 1.25, colors.black)

        def fmthr(hr):
            return "{:.1f}".format(hr) if hr else ""

        def render_row(secs, project, bold_last=False):
            columns = [""]*31 + [fmthr(sum(secs)), project]
            for i, sec in enumerate(secs):
                columns[i] = fmthr(sec)
            if bold_last:
                columns[-1] = b(columns[-1])
            return columns

        stripe_idx = 1

        def stripe():
            nonlocal stripe_idx
            if stripe_idx % 2 == 0:
                ts.row_style('BACKGROUND', 0, -1, colors.HexColor(0xCCFFFF))
            stripe_idx += 1

        project_rows = 12
        for project, secs in self.projects.items():
            ts.row(*render_row(secs, project))
            stripe()
            project_rows -= 1

        while project_rows > 0:
            ts.row("")
            stripe()
            project_rows -= 1

        for key, name in Timer.KIND_CHOICES:
            if key == 'work': continue
            ts.row(*render_row(self.special[key], name))
            stripe()

        # Calculate Overhead
        for idx, total in enumerate(self.totals):
            if total > Decimal(8):
                self.totals[idx] = Decimal(8)
                self.overhead[idx] = total - Decimal(8)
            elif total > Decimal(0):
                self.overhead[idx] = total - Decimal(8)

        ts.row(*render_row(self.totals, _("Total")))
        ts.row_style('LINEABOVE', 0, -1, 1.25, colors.black)
        ts.row(*render_row(self.overhead, _("Overhead")))

        return ts.get_table(colWidths=[(available_width-132)/31]*31+[32, 100], rowHeights=18)


def get_timesheets(qs, year, month):
    sheets = {}
    for timer in qs:
        sheet = sheets.get(timer.user_id)
        if not sheet:
            sheet = sheets[timer.user_id] = TimeSheet(timer.user, year, month)
        sheet.add(timer)
    return sheets.values()


def get_time_sheet_reports(qs, report_date, available_width, available_height, font):
    time_sheet_date = date_format(report_date, "F Y", use_l10n=True)
    for time_sheet in get_timesheets(qs, report_date.year, report_date.month):
        yield Paragraph('{}, {}, {}'.format(
            time_sheet.user.last_name,
            time_sheet.user.first_name,
            time_sheet_date),
            font.h2)
        yield Spacer(0, 4*mm)
        yield time_sheet.get_table(available_width, font)
        yield PageBreak()


def render(qs, letterhead, report_date):
    with BytesIO() as buffer:
        font = FontManager(letterhead.font)
        available_width, available_height, pagesize = get_available_width_height_and_pagesize(letterhead)
        doc = NumberedSystoriDocument(buffer, pagesize=pagesize, debug=DEBUG_DOCUMENT)
        flowables = get_time_sheet_reports(qs, report_date, available_width, available_height, font)
        doc.build(list(flowables), NumberedLetterheadCanvas.factory(letterhead), letterhead)
        return buffer.getvalue()
