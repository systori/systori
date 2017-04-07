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

from systori.lib.templatetags.customformatting import zeroblank, hours, workdays
from ..utils import get_weekday_names_numbers_and_mondays

DEBUG_DOCUMENT = False  # Shows boxes in rendered output


CATEGORIES = [p[0] for p in Timer.KIND_CHOICES if p[0] != Timer.WORK]


def create_timesheet_table(json, available_width, font):

    start = json['first_weekday']
    days = json['total_days']
    names, numbers, mondays = get_weekday_names_numbers_and_mondays(start, days)
    names.append(_("Total"))

    ts = TableStyler(font, base_style=False)
    ts.style.append(('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black))
    ts.style.append(('LINEAFTER', (30, 0), (30, -1), 1.5, colors.black))
    ts.style.append(('BOX', (0, 0), (-1, -1), 0.25, colors.black))
    ts.style.append(('LEFTPADDING', (0, 0), (-2, -1), 2))
    ts.style.append(('RIGHTPADDING', (0, 0), (-2, -1), 2))
    ts.style.append(('ALIGN', (0, 2), (-2, -1), "RIGHT"))
    ts.style.append(('VALIGN', (0, 2), (-2, -1), "MIDDLE"))

    ts.style.append(('FONTSIZE', (0, 0), (-1, 1), 8))  # table header
    ts.style.append(('FONTSIZE', (-1, 2), (-1, -1), 8))  # row type names
    ts.style.append(('FONTSIZE', (0, 2), (-2, -1), 8))  # body

    for monday in mondays:
        ts.style.append(('LINEBEFORE', (monday, 0), (monday, -1), 1.5, colors.black))

    ts.row(*numbers)
    ts.row_style('ALIGNMENT', 0, -1, "CENTER")

    ts.row(*names)
    ts.row_style('ALIGNMENT', 0, -1, "CENTER")
    ts.row_style('LINEBELOW', 0, -1, 1.25, colors.black)

    def render_row(days, total, name):
        columns = [""]*31 + [hours(zeroblank(total)), name]
        for i, mins in enumerate(days):
            columns[i] = hours(zeroblank(mins))
        return columns

    stripe_idx = 1

    def stripe():
        nonlocal stripe_idx
        if stripe_idx % 2 == 0:
            ts.row_style('BACKGROUND', 0, -1, colors.HexColor(0xCCFFFF))
        stripe_idx += 1

    lookup = dict(Timer.KIND_CHOICES)
    lookup.update({
        'payables': _('Total'),
        'overtime': _('Overtime'),
        'compensation': _('Compensation'),
    })
    row_types = [
        'work', 'vacation', 'sick', 'public_holiday',
        'paid_leave', 'unpaid_leave', 'payables',
        'overtime', 'compensation',
    ]
    for row in row_types:
        stripe()
        ts.row(*render_row(json[row], json[row+'_total'], lookup[row]))
        if row == 'payables':
            ts.row_style('LINEABOVE', 0, -1, 1.5, colors.black)
        if row == 'compensation':
            ts.row_style('LINEABOVE', 0, -1, 1.5, colors.black)

    max_days = 31
    last_columns = [32, 65]  # total, row types
    day_columns = [(available_width-sum(last_columns))/max_days]*max_days
    return ts.get_table(colWidths=day_columns+last_columns, rowHeights=18)


def create_rolling_balances(month, json, font):
    ts = TableStyler(font, base_style=False)
    ts.style.append(('GRID', (0, 0), (-1, -1), 0.25, colors.black))
    ts.row("", pgettext_lazy("timesheet", "Previous"), pgettext_lazy("timesheet", "Correction"), month,
           b(pgettext_lazy("timesheet", "Balance"), font))
    ts.row(
        _("Vacation"),
        workdays(zeroblank(json['vacation_transferred'])),
        workdays(zeroblank(json['vacation_correction'])),
        "{}{}".format(
            workdays(json['vacation_net']),
            " ({} - {})".format(
                workdays(json['vacation_added']),
                workdays(json['vacation_total'])
            ) if json['vacation_total'] != 0 else ""
        ),
        b(workdays(json['vacation_balance']), font)
    )
    ts.row(
        _("Overtime"),
        hours(zeroblank(json['overtime_transferred'])),
        hours(zeroblank(json['overtime_correction'])),
        "{}{}".format(
            hours(json['overtime_net']),
            " ({} - {})".format(
                hours(json['overtime_total']),
                hours(json['paid_leave_total'])
            ) if json['paid_leave_total'] != 0 else ""
        ),
        b(hours(json['overtime_balance']), font)
    )
    ts.row(
        _("Compensation"),
        "",
        hours(zeroblank(json['work_correction'])),
        "{}{}".format(
            hours(json['compensation_total']),
            " ({} - {})".format(
                hours(json['payables_total']),
                hours(json['overtime_total'])
            ) if json['overtime_total'] != 0 else ""
        ),
        b(hours(json['compensation_final']), font)
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
        self.payables = [0]*self.total_days
        self.overtime = [0]*self.total_days
        self.compensation = [0]*self.total_days
        self.errors = []
        self.calculated = False

    def add(self, timer):
        days = getattr(self, timer.kind)
        days[timer.started.day-1] += timer.duration

    def calculate(self):
        assert not self.calculated

        for day in range(self.total_days):

            # Work is capped to 8hrs
            work = min(self.work[day], Timer.WORK_HOURS)

            # Payables sans work and consumed overtime (paid_leave)
            payable = sum([
                self.sick[day],
                self.vacation[day],
                self.public_holiday[day],
            ])

            # Total is sum of all the different payables
            # plus the unpaid_leave hours that must be
            # accounted for before we can determine overtime.
            total = self.work[day] + payable + self.unpaid_leave[day]

            # Days with no timers at all are skipped.
            if (total + self.paid_leave[day]) == 0:
                continue

            if total > Timer.WORK_HOURS:
                if self.work[day] > Timer.WORK_HOURS:
                    self.overtime[day] = self.work[day] - Timer.WORK_HOURS
                else:
                    self.overtime[day] = min(self.work[day], total - Timer.WORK_HOURS)

            if (day + self.first_weekday) % 7 in (5, 6):  # 5: Sat, 6: Sun
                # weekends go directly to overtime
                self.payables[day] = self.work[day] + payable + self.paid_leave[day]
                self.overtime[day] = self.payables[day]
                self.compensation[day] = 0
            else:
                self.paid_leave[day] = max(self.paid_leave[day], Timer.WORK_HOURS - total)
                self.payables[day] = self.work[day] + payable + self.paid_leave[day]
                self.compensation[day] = work + payable + self.paid_leave[day]

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

            'payables': self.payables,
            'payables_total': sum(self.payables),
            'overtime': self.overtime,
            'overtime_total': sum(self.overtime),
            'compensation': self.compensation,
            'compensation_total': sum(self.compensation),
        }


def serialize(timers, year, month):
    """ Timers must all be for the same worker and within a single month. """

    data = {}

    collector = TimeSheetCollector(year, month)

    for timer in timers:

        assert timer.started.year == year
        assert timer.started.month == month

        if 'worker_id' not in data:
            data['worker_id'] = timer.worker_id
            data['first_name'] = timer.worker.first_name
            data['last_name'] = timer.worker.last_name
        else:
            assert data['worker_id'] == timer.worker_id

        collector.add(timer)

    data.update(collector.data)
    return data
