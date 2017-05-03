from io import BytesIO
from datetime import date

from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle, PageBreak
from reportlab.lib import colors

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.lib.templatetags.customformatting import ubrdecimal

from .style import p, b, br, nr
from .style import get_available_width_height_and_pagesize
from .style import LetterheadCanvas, SystoriDocument
from .font import FontManager


DEBUG_DOCUMENT = False  # Shows boxes in rendered output


def render(project, letterhead, title):

    with BytesIO() as buffer:

        font = FontManager(letterhead.font)

        available_width, available_height, pagesize = get_available_width_height_and_pagesize(letterhead)

        proposal_date = date_format(date.today(), use_l10n=True)

        doc = SystoriDocument(buffer, pagesize=pagesize, debug=DEBUG_DOCUMENT)

        COLS = 55
        ROWS = 23

        pages = []

        for job in project.jobs.all():
            for taskgroup in job.groups.all():
                for task in taskgroup.tasks.all():

                    pages.append(Table([[b(_('Evidence Sheet'), font), nr(proposal_date, font)]]))

                    pages.append(Table([
                        [b(_('Project'), font), p('%s / %s / %s' % (job.project, job.name, taskgroup.name), font)]
                    ],
                        colWidths=[30*mm, None],
                        style=[
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ]
                    ))

                    pages.append(Table([
                        [b(_('Code'), font), p(task.code.strip(), font),
                         br(_('Task'), font), p(task.name[:60].strip(), font)],
                        [b(_('P-Amount'), font), p('%s %s' % (ubrdecimal(task.qty).strip(), task.unit.strip()), font)]
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
            pages.append(b(_('There are no billable Tasks available.'), font))

        doc.build(pages, title, LetterheadCanvas.factory(letterhead), letterhead)

        return buffer.getvalue()
