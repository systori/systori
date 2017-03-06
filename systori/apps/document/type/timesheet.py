from io import BytesIO

from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer, PageBreak
from reportlab.lib import colors

from django.utils.formats import date_format
from django.utils.translation import pgettext_lazy, ugettext_lazy as _

from systori.apps.timetracking.models import Timer

import calendar

from .style import SystoriDocument, TableStyler
from .style import LetterheadCanvas
from .style import get_available_width_height_and_pagesize, b
from .font import FontManager

from systori.lib.templatetags.customformatting import todecimalhours,\
    dayshoursgainedverbose, dayshours, workdaysverbose, hoursverbose, hoursdays

DEBUG_DOCUMENT = False  # Shows boxes in rendered output


WEEKDAYS = [_('Mon'), _('Tue'), _('Wed'), _('Thu'), _('Fri'), _('Sat'), _('Sun')]
CATEGORIES = [p[0] for p in Timer.KIND_CHOICES if p[0] != Timer.WORK]


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

    ts = TableStyler(font, base_style=False)
    ts.style.append(('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black))
    ts.style.append(('LINEAFTER', (30, 0), (30, -1), 1.5, colors.black))
    ts.style.append(('BOX', (0, 0), (-1, -1), 0.25, colors.black))
    ts.style.append(('FONTSIZE', (0, 0), (-2, 1), 9))
    ts.style.append(('LEFTPADDING', (0, 0), (-2, -1), 2))
    ts.style.append(('RIGHTPADDING', (0, 0), (-2, -1), 2))
    ts.style.append(('ALIGNMENT', (0, 2), (-2, -1), "CENTER"))

    for monday in mondays:
        ts.style.append(('LINEBEFORE', (monday, 0), (monday, -1), 1.5, colors.black))

    ts.row(*numbers)
    ts.row_style('ALIGNMENT', 0, -1, "CENTER")

    ts.row(*names)
    ts.row_style('ALIGNMENT', 0, -1, "CENTER")
    ts.row_style('LINEBELOW', 0, -1, 1.25, colors.black)

    def render_row(days, total, name):
        columns = [""]*31 + [(todecimalhours(total) if total else ''), name]
        for i, sec in enumerate(days):
            columns[i] = (todecimalhours(sec) if sec else '')
        return columns

    stripe_idx = 1

    def stripe():
        nonlocal stripe_idx
        if stripe_idx % 2 == 0:
            ts.row_style('BACKGROUND', 0, -1, colors.HexColor(0xCCFFFF))
        stripe_idx += 1

    lookup = dict(Timer.KIND_CHOICES)
    lookup.update({
        'compensation': _('Compensation'),
        'overtime': _('Overtime')
    })
    row_types = [
        'work', 'vacation', 'sick', 'public_holiday',
        'paid_leave', 'unpaid_leave', 'compensation',
        'overtime'
    ]
    for row in row_types:
        stripe()
        if row == 'overtime':
            ts.row_style('LINEABOVE', 0, -1, 1.25, colors.black)
        ts.row(*render_row(json[row], json[row+'_total'], lookup[row]))

    return ts.get_table(colWidths=[(available_width-132)/31]*31+[32, 100], rowHeights=18)


def create_rolling_balances(month, json, font):
    ts = TableStyler(font, base_style=False)
    ts.style.append(('GRID', (0, 0), (-1, -1), 0.25, colors.black))
    ts.row("", pgettext_lazy("timesheet", "Previous"), pgettext_lazy("timesheet", "Correction"), month,
           b(pgettext_lazy("timesheet", "Balance"), font))
    ts.row(
        _("Vacation"),
        (workdaysverbose(json['vacation_transferred']) if json['vacation_transferred'] != 0 else ''),
        (workdaysverbose(json['vacation_correction']) if json['vacation_correction'] != 0 else '' ),
        dayshoursgainedverbose(json['vacation_total']),
        b(dayshours(json['vacation_balance']), font)
    )
    ts.row(
        _("Overtime"),
        (hoursverbose(json['overtime_transferred']) if json['overtime_transferred'] != 0 else ''),
        (hoursverbose(json['overtime_correction']) if json['overtime_correction'] != 0 else ''),
        (hoursverbose(json['overtime_total']) if json['overtime_total'] != 0 else ''),
        (b(hoursdays(json['overtime_balance']), font) if json['overtime_balance'] != 0 else '')
    )
    ts.row(
        pgettext_lazy("timesheet", "Final Total"),
        '',
        (hoursverbose(json['work_correction']) if json['work_correction'] else ''),
        hoursverbose(json['work_total']),
        b(hoursverbose(json['work_balance']), font)
    )
    return ts.get_table(colWidths=[90]*3+[152]+[132], rowHeights=18, hAlign='RIGHT')


def create_signature(json, font):
    ts = TableStyler(font, base_style=False)
    ts.row(pgettext_lazy("timesheet", "Approved") + ": ")
    ts.style.append(('INNERGRID', (0, 0), (0, 1), 0.25, colors.black))

    return ts.get_table(colWidths=[284], rowHeights=22, hAlign='RIGHT')


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
        yield create_signature(json, font)
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
        # timers
        self.work = [0]*self.total_days
        self.vacation = [0]*self.total_days
        self.sick = [0]*self.total_days
        self.public_holiday = [0]*self.total_days
        self.paid_leave = [0]*self.total_days
        self.unpaid_leave = [0]*self.total_days
        # calculated
        self.compensation = [0]*self.total_days
        self.overtime = [0]*self.total_days
        self.errors = []
        self.calculated = False

    def add(self, timer):
        days = getattr(self, timer.kind)
        days[timer.date.day-1] += timer.duration

    def calculate(self):
        assert not self.calculated

        for day in range(self.total_days):

            # Work is capped at 8hrs.
            work = self.work[day]
            if self.work[day] > Timer.WORK_HOURS:
                work = Timer.WORK_HOURS

            # Basic payables excluding paid/unpaid leave.
            payable = sum([
                work,
                self.sick[day],
                self.vacation[day],
                self.public_holiday[day],
            ])

            if (payable+self.paid_leave[day]) == 0:
                # Day has nothing, skip it.
                continue

            total = payable + self.unpaid_leave[day]

            overtime = 0

            if total < Timer.WORK_HOURS:
                # All of the payables + unpaid
                # did not add up to full work day
                # leads to negative overtime.
                overtime = total - Timer.WORK_HOURS

            elif self.work[day] > Timer.WORK_HOURS:
                # Work hours is greater than full day
                # leads to accumulated overtime.
                overtime = self.work[day] - Timer.WORK_HOURS

            # Overtime and paid_leave are two sides of the same coin.
            # Overtime is calculated based on other payables and
            # paid_leave is manually set as PAID_LEAVE timers.
            # They have opposite parity.
            if -overtime > self.paid_leave[day]:
                # Calculated overtime was larger than manual paid_leave.
                # For example, work is 6hrs, paid_leave is 1hr, that means
                # overtime would be -2. We need to override paid_leave
                # to be 2hrs to balance the equation.
                self.paid_leave[day] = -overtime
            elif overtime < -self.paid_leave[day]:
                # Calculated overtime is less than the manually defined paid_leave.
                # In this case the manual overrides the calculated.
                overtime = -self.paid_leave[day]

            self.overtime[day] = overtime
            self.compensation[day] = payable + self.paid_leave[day]

        self.calculated = True

    @property
    def data(self):
        if not self.calculated:
            self.calculate()
        return {
            'first_weekday': self.first_weekday,
            'total_days': self.total_days,

            'work': self.work,
            'work_total': sum(self.work),
            'vacation': self.vacation,
            'vacation_total': sum(self.vacation),
            'sick': self.sick,
            'sick_total': sum(self.sick),
            'public_holiday': self.public_holiday,
            'public_holiday_total': sum(self.public_holiday),
            'paid_leave': self.paid_leave,
            'paid_leave_total': sum(self.paid_leave),
            'unpaid_leave': self.unpaid_leave,
            'unpaid_leave_total': sum(self.unpaid_leave),

            'compensation': self.compensation,
            'compensation_total': sum(self.compensation),
            'overtime': self.overtime,
            'overtime_total': sum(self.overtime),
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
