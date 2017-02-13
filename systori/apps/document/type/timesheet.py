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


WEEKDAYS = [_('Mon'), _('Tue'), _('Wed'), _('Thu'), _('Fri'), _('Sat'), _('Sun')]
CATEGORIES = [p[0] for p in Timer.KIND_CHOICES if p[0] != Timer.WORK]


def fmthr(sec):
    return "{:.1f}".format(sec/60.0/60.0) if sec else ""


def create_timesheet_table(json, available_width, font):

    start = json['first_weekday']
    days = json['total_days']

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

    def render_row(days, total, name):
        columns = [""]*31 + [fmthr(total), name]
        for i, sec in enumerate(days):
            columns[i] = fmthr(sec)
        return columns

    stripe_idx = 1

    def stripe():
        nonlocal stripe_idx
        if stripe_idx % 2 == 0:
            ts.row_style('BACKGROUND', 0, -1, colors.HexColor(0xCCFFFF))
        stripe_idx += 1

    project_rows = 3
    for project in json['projects']:
        ts.row(*render_row(project['days'], project['total'], project['name']))
        stripe()
        project_rows -= 1

    while project_rows > 0:
        ts.row("")
        stripe()
        project_rows -= 1

    kind_choices = dict(Timer.KIND_CHOICES)
    for special in json['special']:
        ts.row(*render_row(special['days'], special['total'], kind_choices[special['name']]))
        stripe()

    ts.row(*render_row(json['holiday'], json['holiday_total'], _('Holiday')))
    stripe()

    ts.row(*render_row(json['work'], json['work_total'], _("Total")))
    ts.row_style('LINEABOVE', 0, -1, 1.25, colors.black)
    ts.row(*render_row(json['overtime'], json['overtime_total'], _("Overtime")))

    return ts.get_table(colWidths=[(available_width-132)/31]*31+[32, 100], rowHeights=18)


def create_rolling_balances(month, json, font):
    ts = TableStyler(font, base_style=False)
    ts.style.append(('GRID', (0, 0), (-1, -1), 0.25, colors.black))
    ts.row("", _("Previous"), "", month, _("Balance"))
    ts.row(_("Holiday"), fmthr(json['holiday_transferred']), fmthr(json['holiday_correction']), fmthr(json['holiday_total']), fmthr(json['holiday_balance']))
    ts.row(_("Overtime"), fmthr(json['overtime_transferred']), fmthr(json['overtime_correction']), fmthr(json['overtime_total']), fmthr(json['overtime_balance']))
    return ts.get_table(colWidths=[100, 100, 32, 80, 100], rowHeights=18, hAlign='RIGHT')


def create_final_total(json, font):
    ts = TableStyler(font, base_style=False)
    ts.style.append(('GRID', (0, 0), (-1, -1), 1, colors.black))
    ts.row(b(_("Final Total"), font), fmthr(json['work_correction']), b(fmthr(json['work_balance']), font), _("Approved")+": "+'_'*8)
    return ts.get_table(colWidths=[100, 32, 80, 100], rowHeights=18, hAlign='RIGHT')


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
        yield Spacer(0, 4*mm)
        yield create_rolling_balances(date_format(timesheet.document_date, "F", use_l10n=True), json, font)
        yield Spacer(0, 4*mm)
        yield create_final_total(json, font)
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
            (c, {'name': c, 'days': [0]*self.total_days, 'total': 0})
            for c in [p[0] for p in Timer.KIND_CHOICES if p[0] not in (Timer.WORK, Timer.HOLIDAY)]
        ])
        self.work = [0]*self.total_days
        self.work_total = 0
        self.overtime = [0]*self.total_days
        self.overtime_total = 0
        self.holiday = [0]*self.total_days
        self.holiday_total = 0

    def add(self, timer):
        day_idx = timer.date.day-1
        category = timer.kind

        slot = None
        if category == Timer.WORK:
            slot = self.projects.setdefault(
                None, {'name': '', 'days': [0]*self.total_days, 'total': 0}
            )
        elif category in self.special:
            slot = self.special[category]

        if slot:
            slot['days'][day_idx] += timer.duration
            slot['total'] += timer.duration

        if category == timer.HOLIDAY:
            self.holiday[day_idx] += timer.duration
            self.holiday_total += timer.duration

        if category != timer.UNPAID_LEAVE:
            self.work[day_idx] += timer.duration

    @property
    def data(self):
        # Calculate Overtime
        for idx, total in enumerate(self.work):
            if total > Timer.WORK_HOURS:
                self.work[idx] = Timer.WORK_HOURS
                self.work_total += Timer.WORK_HOURS
                self.overtime[idx] = total - Timer.WORK_HOURS
            elif total > 0:
                self.work_total += total
                self.overtime[idx] = total - Timer.WORK_HOURS
            self.overtime_total += self.overtime[idx]
        return {
            'first_weekday': self.first_weekday,
            'total_days': self.total_days,
            'projects': list(self.projects.values()),
            'special': list(self.special.values()),

            'work': self.work,
            'work_total': self.work_total,
            'work_correction': 0,
            'work_correction_notes': '',
            'work_balance': 0,

            'overtime': self.overtime,
            'overtime_total': self.overtime_total,
            'overtime_transferred': 0,
            'overtime_correction': 0,
            'overtime_correction_notes': '',
            'overtime_balance': 0,

            'holiday': self.holiday,
            'holiday_total': self.holiday_total,
            'holiday_added':  0,
            'holiday_transferred':  0,
            'holiday_correction': 0,
            'holiday_correction_notes': '',
            'holiday_balance': 0,
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
