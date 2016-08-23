from io import BytesIO
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

from .style import NumberedSystoriDocument, TableFormatter, ContinuationTable
from .style import chunk_text, force_break, p, b, br
from .style import NumberedLetterheadCanvas, NumberedCanvas
from .style import get_available_width_height_and_pagesize
from .style import heading_and_date, get_address_label, get_address_label_spacer
from .font import FontManager


DEBUG_DOCUMENT = False  # Shows boxes in rendered output


class TimeSheet:

    WEEKDAYS = [_('Mon'), _('Tue'), _('Wed'), _('Thu'), _('Fri'), _('Sat'), _('Sun')]

    def __init__(self, year, month):
        self.names = []
        self.numbers = []
        start, self.days = calendar.monthrange(year, month)
        for day in range(31):
            if day < self.days:
                self.names.append(self.WEEKDAYS[(day+start) % 7])
                self.numbers.append(str(day+1))
            else:
                self.names.append("")
                self.numbers.append("")
        self.names.append(_("Total"))
        self.names.append(_("Project"))
        self.projects = OrderedDict()
        self.special = OrderedDict([
            (p, [0]*self.days) for p in ['holiday', 'illness', 'correction', 'education']
        ])

    def add(self, date, project, seconds):
        slot = None
        if project in self.special:
            slot = self.special[project]
        elif project in self.projects:
            slot = self.projects[project]
        else:
            slot = self.projects[project] = [0]*self.days

        slot[date.day-1] += seconds


    @property
    def data(self):
        yield self.numbers
        yield self.names

        def secs_to_hrs(secs):
            return str(round(secs / 60.0 / 60.0, 1) or "")

        def render_row(secs, project):
            total = sum(secs)
            columns = [""]*31 + [secs_to_hrs(total), project]
            for i, sec in enumerate(secs):
                columns[i] = secs_to_hrs(sec)
            return columns

        project_rows = 10
        for project, secs in self.projects.items():
            yield render_row(secs, project)
            project_rows -= 1

        while project_rows > 0:
            yield [""]
            project_rows -= 1

        yield render_row(self.special['holiday'], _("Holiday"))
        yield render_row(self.special['illness'], _("Illness"))
        yield render_row(self.special['correction'], _("Correction"))
        yield render_row(self.special['education'], _("Education"))


def collate_elements(data, month, year, available_width, available_height, font):

    ts = TimeSheet(year, month)
    for date, projects in data.items():
        for name, stats in projects.items():
            if stats['duration'] > 0:
                ts.add(date, name, stats['duration'])

    table = Table(list(ts.data), colWidths=[(available_width-135)/31]*31+[35, 100], rowHeights=18)
    table.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('FONTSIZE', (0, 0), (-3, 1), 9),
        ('LEFTPADDING', (0, 0), (-3, -1), 2),
    ]))

    return [table]


def render(data, letterhead, month, year):

    with BytesIO() as buffer:

        font = FontManager(letterhead.font)

        available_width, available_height, pagesize = get_available_width_height_and_pagesize(letterhead)

        proposal_date = date_format(date.today(), use_l10n=True)

        doc = NumberedSystoriDocument(buffer, pagesize=pagesize, debug=DEBUG_DOCUMENT)

        flowables = [

            heading_and_date(_('Monthly hours report for {}'.format(date_format(date(year, month, 1), "F Y", use_l10n=True))),
                             proposal_date, font, available_width, debug=DEBUG_DOCUMENT),

            Spacer(0, 4*mm),

        ] + collate_elements(data, month, year, available_width, available_height, font)

        doc.build(flowables, NumberedLetterheadCanvas.factory(letterhead), letterhead)

        return buffer.getvalue()
