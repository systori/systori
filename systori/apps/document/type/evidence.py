from io import BytesIO
from datetime import date

from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle, PageBreak
from reportlab.lib import colors

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.lib.templatetags.customformatting import ubrdecimal
from systori.apps.project.models import Project
from systori.apps.task.models import Job

from .style import p, b, br, nr
from .style import get_available_width_height_and_pagesize
from .style import LetterheadCanvas, SystoriDocument
from .font import FontManager


DEBUG_DOCUMENT = False  # Shows boxes in rendered output

COLS = 55
ROWS = 25

def render(instance, letterhead):

    with BytesIO() as buffer:

        font = FontManager(letterhead.font)

        available_width, available_height, pagesize = get_available_width_height_and_pagesize(letterhead)

        proposal_date = date_format(date.today(), use_l10n=True)

        doc = SystoriDocument(buffer, pagesize=pagesize, debug=DEBUG_DOCUMENT)

        pages = []

        render_evidence_pages(instance, pages, font, proposal_date)

        if not pages:
            pages.append(b(_('There are no billable Tasks available.'), font))

        doc.build(pages, LetterheadCanvas.factory(letterhead), letterhead)

        return buffer.getvalue()



def render_evidence_pages(instance, pages, font, proposal_date):

    project_data = {
        'project_pk': str(instance.id),
        'code': "",
        'name': instance.name,
        'id': instance.id,
        'jobs': [],
    }
    if isinstance(instance, Project):
        for job in instance.jobs.all():
            job_instance = {
                'code': job.code,
                'name': job.name,
                'groups': [],
                'tasks': [],
            }
            project_data['jobs'].append(job_instance)

            _serialize_project(project_data, job_instance, job, pages, font, proposal_date)

    if isinstance(instance, Job):
        project_data["project_pk"] = str(instance.project.id)
        job_instance = {
            'code': instance.code,
            'name': instance.name,
            'groups': [],
            'tasks': [],
        }
        project_data['jobs'].append(job_instance)

        _serialize_project(project_data, job_instance, instance, pages, font, proposal_date)

    return None


def _serialize_project(project_data, data, parent, pages, font, proposal_date):

    for group in parent.groups.all():
        group_dict = {
            'code': group.code,
            'name': group.name,
            'tasks': [],
            'groups': [],
        }
        data['groups'].append(group_dict)

        _serialize_project(project_data, group_dict, group, pages, font, proposal_date)

    for task in parent.tasks.all():
        task_description = " / ".join([project_data['code'] +" "+ project_data['name'],
                                       data['code'] +" "+ data['name']])[:110]

        pages.append(Table([
            [b(_('Evidence Sheet'), font), br(_('Sheet-No')+':', font), nr('...............', font)]
        ],
            colWidths=[None, 50 * mm, 35* mm]))

        pages.append(Table([
            [p(task_description, font), br(' #%s' % project_data['project_pk'], font), nr(proposal_date, font)],
        ],
            colWidths=[None, 20 * mm, 35* mm],
            style=[
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ]
        ))

        pages.append(Table([
            [b(_('Task'), font), p(task.code.strip() +' '+ task.name[:60].strip(), font),
             br(_('P-Amount'), font), nr('%s %s' % (ubrdecimal(task.qty).strip(), task.unit.strip()), font)]
        ],
            colWidths=[20 * mm, None, 35 * mm, 35 * mm],
            style=[
            ]
        ))

        t = Table([[''] * COLS] * ROWS, colWidths=[5 * mm] * COLS, rowHeights=[5 * mm] * ROWS)
        t.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey)
        ]))
        pages.append(t)

        pages.append(PageBreak())
