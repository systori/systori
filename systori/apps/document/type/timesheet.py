import os
import calendar
from itertools import chain

from django.conf import settings
from django.utils.translation import ugettext as _
from django.template.loader import get_template, render_to_string

from bericht.pdf import PDFStreamer
from bericht.html import HTMLParser, CSS

from systori.apps.timetracking.models import Timer
from ..utils import get_weekday_names_numbers_and_mondays


class TimesheetRenderer:
    def __init__(self, timesheets, letterhead):
        self.timesheets = timesheets
        self.letterhead = letterhead

        # cache template lookups
        self.timesheet_html = get_template("document/timesheet.html")

    @property
    def pdf(self):
        return PDFStreamer(
            HTMLParser(self.generate, CSS(self.css)),
            os.path.join(settings.MEDIA_ROOT, self.letterhead.letterhead_pdf.name),
            "landscape",
        )

    @property
    def html(self):
        return "".join(chain(("<style>", self.css, "</style>"), self.generate()))

    @property
    def css(self):
        return render_to_string(
            "document/timesheet.css", {"letterhead": self.letterhead}
        )

    def generate(self):
        lookup = dict(Timer.KIND_CHOICES)
        lookup.update(
            {
                "payables": _("Total"),
                "overtime": _("Overtime"),
                "compensation": _("Compensation"),
            }
        )
        for timesheet in self.timesheets:
            json = timesheet.json
            context = {"timesheet": timesheet, "document_date": timesheet.document_date}
            context.update(json)
            context["daynames"], context["daynumbers"], context[
                "mondays"
            ] = get_weekday_names_numbers_and_mondays(
                json["first_weekday"], json["total_days"], False
            )
            context["rows"] = [
                (t, lookup[t], json[t], json[t + "_total"])
                for t in [
                    "work",
                    "vacation",
                    "sick",
                    "public_holiday",
                    "paid_leave",
                    "unpaid_leave",
                    "payables",
                    "overtime",
                    "compensation",
                ]
            ]
            yield self.timesheet_html.render(context)


class TimeSheetCollector:
    def __init__(self, year, month):
        self.first_weekday, self.total_days = calendar.monthrange(year, month)
        # timers
        self.work = [0] * self.total_days
        self.vacation = [0] * self.total_days
        self.sick = [0] * self.total_days
        self.public_holiday = [0] * self.total_days
        self.paid_leave = [0] * self.total_days
        self.unpaid_leave = [0] * self.total_days
        # calculated
        self.payables = [0] * self.total_days
        self.overtime = [0] * self.total_days
        self.compensation = [0] * self.total_days
        self.errors = []
        self.calculated = False

    def add(self, timer):
        days = getattr(self, timer.kind)
        days[timer.started.day - 1] += timer.duration

    def calculate(self):
        assert not self.calculated

        for day in range(self.total_days):

            # Work is capped to 8hrs
            work = min(self.work[day], Timer.WORK_HOURS)

            # Payables sans work and consumed overtime (paid_leave)
            payable = sum(
                [self.sick[day], self.vacation[day], self.public_holiday[day]]
            )

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
                self.paid_leave[day] = max(
                    self.paid_leave[day], Timer.WORK_HOURS - total
                )
                self.payables[day] = self.work[day] + payable + self.paid_leave[day]
                self.compensation[day] = work + payable + self.paid_leave[day]

        self.calculated = True

    @property
    def data(self):
        if not self.calculated:
            self.calculate()
        return {
            "first_weekday": self.first_weekday,
            "total_days": self.total_days,
            "work": self.work,
            "work_total": sum(self.work),
            "vacation": self.vacation,
            "vacation_total": sum(self.vacation),
            "sick": self.sick,
            "sick_total": sum(self.sick),
            "public_holiday": self.public_holiday,
            "public_holiday_total": sum(self.public_holiday),
            "paid_leave": self.paid_leave,
            "paid_leave_total": sum(self.paid_leave),
            "unpaid_leave": self.unpaid_leave,
            "unpaid_leave_total": sum(self.unpaid_leave),
            "payables": self.payables,
            "payables_total": sum(self.payables),
            "overtime": self.overtime,
            "overtime_total": sum(self.overtime),
            "compensation": self.compensation,
            "compensation_total": sum(self.compensation),
        }


def serialize(timers, year, month):
    """ Timers must all be for the same worker and within a single month. """

    data = {}

    collector = TimeSheetCollector(year, month)

    for timer in timers:

        assert timer.started.year == year
        assert timer.started.month == month

        if "worker_id" not in data:
            data["worker_id"] = timer.worker_id
            data["first_name"] = timer.worker.first_name
            data["last_name"] = timer.worker.last_name
        else:
            assert data["worker_id"] == timer.worker_id

        collector.add(timer)

    data.update(collector.data)
    return data
