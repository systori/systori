from io import BytesIO
from decimal import Decimal
from datetime import date
from collections import OrderedDict

from reportlab.lib.units import mm, cm
from reportlab.platypus import Paragraph, Spacer, KeepTogether, PageBreak, Table, TableStyle
from reportlab.lib import colors

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.apps.timetracking.models import Timer
from systori.apps.timetracking.utils import format_seconds

import calendar

from .style import SystoriDocument, TableStyler
from .style import chunk_text, force_break, p, b, br
from .style import LetterheadCanvas
from .style import get_available_width_height_and_pagesize
from .font import FontManager


DEBUG_DOCUMENT = False  # Shows boxes in rendered output


def seconds_to_hours(seconds):
    return Decimal(seconds / 60.0 / 60.0)


WEEKDAYS = [_('Mon'), _('Tue'), _('Wed'), _('Thu'), _('Fri'), _('Sat'), _('Sun')]
CATEGORIES = [p[0] for p in Timer.KIND_CHOICES if p[0] != Timer.WORK]


def create_timesheet_table(json, available_width, font):

    start = json['first_weekday']
    days = json['total_days']
    projects = json['projects']
    special = json['special']
    totals = json['totals']
    overhead = json['overhead']

    names = []
    numbers = []
    mondays = []
    for day in range(31):
        if day < days:
            names.append(WEEKDAYS[(day+start) % 7])
            if ((day+start) % 7) == 0:
                mondays.append(day)
            numbers.append(str(day+1))
        else:
            names.append("")
            numbers.append("")
    names.append(_("Total"))
    names.append(_("Project"))

    ts = TableStyler(font, base_style=False)
    ts.style.append(('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black))
    ts.style.append(('LINEAFTER', (30, 0), (30, -1), 1.5, colors.black))
    ts.style.append(('BOX', (0, 0), (-1, -1), 0.25, colors.black))
    ts.style.append(('FONTSIZE', (0, 0), (-2, 1), 9))
    ts.style.append(('LEFTPADDING', (0, 0), (-2, -1), 2))
    ts.style.append(('RIGHTPADDING', (0, 0), (-2, -1), 2))
    ts.style.append(('ALIGNMENT', (0, 2), (-2, -1), "RIGHT"))

    for monday in mondays:
        ts.style.append(('LINEBEFORE', (monday, 0), (monday, -1), 1.5, colors.black))

    ts.row(*numbers)
    ts.row_style('ALIGNMENT', 0, -1, "CENTER")

    ts.row(*names)
    ts.row_style('ALIGNMENT', 0, -1, "CENTER")
    ts.row_style('LINEBELOW', 0, -1, 1.25, colors.black)

    def fmthr(hr):
        return "{:.1f}".format(hr) if hr else ""

    def render_row(secs, project, special, bold_last=False):
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

    project_rows = 9
    for project, secs in projects:
        ts.row(*render_row(secs, project))
        stripe()
        project_rows -= 1

    while project_rows > 0:
        ts.row("")
        stripe()
        project_rows -= 1

    kind_choices = dict(Timer.KIND_CHOICES)
    for name, secs in special:
        ts.row(*render_row(secs, kind_choices[name], special))
        stripe()

    ts.row(*render_row(totals, _("Total")))
    ts.row_style('LINEABOVE', 0, -1, 1.25, colors.black)
    ts.row(*render_row(overhead, _("Overhead")))

    return ts.get_table(colWidths=[(available_width-132)/31]*31+[32, 100], rowHeights=18)


def create_timesheets(timesheets, available_width, available_height, font):
    for timesheet in timesheets:
        json = timesheet.json
        yield Paragraph('{}, {}, {}'.format(
            json['last_name'],
            json['first_name'],
            date_format(timesheet.document_date, "F Y", use_l10n=True)),
            font.h2)
        yield Spacer(0, 4*mm)
        yield create_timesheet_table(json, available_width, font)
        yield PageBreak()


def render(timesheets, letterhead):
    with BytesIO() as buffer:
        font = FontManager(letterhead.font)
        available_width, available_height, pagesize = get_available_width_height_and_pagesize(letterhead)
        doc = SystoriDocument(buffer, pagesize=pagesize, debug=DEBUG_DOCUMENT)
        flowables = create_timesheets(timesheets, available_width, available_height, font)
        doc.build(list(flowables), LetterheadCanvas.factory(letterhead), letterhead)
        return buffer.getvalue()


class TimeSheetCollector:

    def __init__(self, year, month):
        self.first_weekday, self.total_days = calendar.monthrange(year, month)
        self.projects = OrderedDict()
        self.special = OrderedDict([
            (c, [Decimal(0)]*self.total_days)
            for c in [p[0] for p in Timer.KIND_CHOICES if p[0] != Timer.WORK]
        ])
        self.totals = [Decimal(0)]*self.total_days
        self.overhead = [Decimal(0)]*self.total_days

    def add(self, timer):
        day_idx = timer.date.day-1
        hours = seconds_to_hours(timer.duration)
        category = timer.kind
        slot = None
        if category == Timer.WORK:
            slot = self.projects.setdefault(None, [Decimal(0)]*self.total_days)
        elif category in self.special:
            slot = self.special[category]
        slot[day_idx] += hours
        self.totals[day_idx] += hours

    @property
    def data(self):
        # Calculate Overhead
        for idx, total in enumerate(self.totals):
            if total > Decimal(8):
                self.totals[idx] = Decimal(8)
                self.overhead[idx] = total - Decimal(8)
            elif total > Decimal(0):
                self.overhead[idx] = total - Decimal(8)
        return {
            'first_weekday': self.first_weekday,
            'total_days': self.total_days,
            'projects': self.projects.items(),
            'special': self.special.items(),
            'totals': self.totals,
            'overhead': self.overhead
        }


def serialize(timers, year, month):
    """ Timers must all be for the same worker and within a single month. """

    data = {}

    collector = TimeSheetCollector(year, month)

    for timer in timers:

        assert timer.date.year == year
        assert timer.date.month == month

        if 'worker_id' not in data:
            data['worker_id'] = timer.worker_id
            data['first_name'] = timer.worker.first_name
            data['last_name'] = timer.worker.last_name
        else:
            assert data['worker_id'] == timer.worker_id

        collector.add(timer)

    data.update(collector.data)
    return data
