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

from .style import p, b, br, nr


DEBUG_DOCUMENT = False  # Shows boxes in rendered output


def render(project):

    with BytesIO() as buffer:

        proposal_date = date_format(date.today(), use_l10n=True)

        COLS = 55
        ROWS = 25

        pages = []

        for job in project.jobs.all():
            for taskgroup in job.taskgroups.all():
                for task in taskgroup.tasks.all():

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
                        [b(_('Code')), p(task.code.strip()),
                         br(_('Task')), p(task.name[:60].strip())],
                        [b(_('P-Amount')), '%s %s' % (ubrdecimal(task.qty).strip(), task.unit.strip()),
                         br(_('UP')), money(task.unit_price).strip()]
                    ],
                        colWidths=[30*mm, 70*mm, 30*mm, None],
                        style=TableStyle([
                            ('SPAN', (3, 0), (-1, 0)),
                        ])
                    ))

                    t = Table([['']*COLS]*ROWS, colWidths=[5*mm]*COLS, rowHeights=[5*mm]*ROWS)
                    t.setStyle(TableStyle([
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey)
                    ]))
                    pages.append(t)

                    pages.append(PageBreak())

        if not pages:
            pages.append(b(_('There are no billable Tasks available.')))

        doc = SimpleDocTemplate(buffer,
                pagesize = landscape(A4),
                topMargin = 20*mm,
                bottomMargin = 34*mm,
                leftMargin = 11*mm,
                rightMargin = 11*mm)

        doc.build(pages, Canvas)

        return buffer.getvalue()
