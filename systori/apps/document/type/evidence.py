from io import BytesIO
from datetime import date

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph, Table, TableStyle, PageBreak
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.lib.templatetags.customformatting import ubrdecimal, money

from .style import LandscapeStationaryCanvas
from .style import p, b, br, nr


DEBUG_DOCUMENT = False  # Shows boxes in rendered output


def render(job):

    with BytesIO() as buffer:

        proposal_date = date_format(date.today(), use_l10n=True)

        COLS = 55
        ROWS = 25

        pages = []

        for taskgroup in job.billable_taskgroups:

            for task in taskgroup.billable_tasks:

                pages.append(Table([[b(_('Evidence Sheet')), nr(proposal_date)]]))

                pages.append(Table([
                    [b(_('Project')), p('%s / %s / %s' % (job.project, job.name, taskgroup.name))]
                ],
                    colWidths=[30*mm, None],
                    style=[
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ]
                ))

                pages.append(Table([
                    [b(_('Code')), p(task.code), br(_('Task')), p(task.name)],
                    [b(_('P-Amount')), p(job.project.name), br(_('Amount')), p(job.project.name), br(_('UP')), money(task.unit_price)]
                ],
                    colWidths=[30*mm, None, None, None, None, None],
                    style=TableStyle([
                        #('ALIGN', (0, 0), (1, -1), 'LEFT'),
                        #('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ])
                ))

                t = Table([['']*COLS]*ROWS, colWidths=[5*mm]*COLS, rowHeights=[5*mm]*ROWS)
                t.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey)
                ]))
                pages.append(t)

                pages.append(PageBreak())

        doc = SimpleDocTemplate(buffer,
                pagesize = landscape(A4),
                topMargin = 20*mm,
                bottomMargin = 34*mm,
                leftMargin = 11*mm,
                rightMargin = 11*mm)

        doc.build(pages, canvasmaker=LandscapeStationaryCanvas)

        return buffer.getvalue()
