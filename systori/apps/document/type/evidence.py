import os.path
from io import BytesIO
from datetime import date

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph, Table, TableStyle, PageBreak
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors

from rlextra.pageCatcher.pageCatcher import storeFormsInMemory, restoreFormsInMemory, open_and_read

from django.conf import settings
from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.lib.templatetags.customformatting import ubrdecimal, money

from .style import SystoriDocument, TableFormatter, ContinuationTable
from .style import stylesheet, chunk_text, force_break, p, b, br, nr
from . import font


DEBUG_DOCUMENT = False  # Shows boxes in rendered output


class StationaryCanvas(Canvas):

    def __init__(self, *args, **kwargs):
        super(StationaryCanvas, self).__init__(*args, **kwargs)
        static_dir = os.path.join(settings.BASE_DIR, 'static')
        cover_pdf_path = os.path.join(static_dir, "softronic2_landscape.pdf")
        cover_pdf = open_and_read(cover_pdf_path)

        self.page_content = storeFormsInMemory(cover_pdf, pagenumbers=[0], prefix='stationary')[1]
        restoreFormsInMemory(self.page_content, self)

    def showPage(self):
        self.doForm('stationary0')
        super(StationaryCanvas, self).showPage()


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

        doc.build(pages, canvasmaker=StationaryCanvas)

        return buffer.getvalue()
