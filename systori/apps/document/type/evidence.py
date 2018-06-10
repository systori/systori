import os
from itertools import chain
from io import BytesIO
from datetime import date

from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle, PageBreak
from reportlab.lib import colors

from django.utils.formats import date_format
from django.utils.translation import ugettext as _
from django.conf import settings
from django.template.loader import get_template, render_to_string

from systori.lib.templatetags.customformatting import ubrdecimal
from systori.apps.project.models import Project
from systori.apps.task.models import Job, Group, Task

from .style import p, b, br, nr
from .style import get_available_width_height_and_pagesize
from .style import LetterheadCanvas, SystoriDocument
from .font import FontManager

from bericht.pdf import PDFStreamer
from bericht.html import HTMLParser, CSS

DEBUG_DOCUMENT = False  # Shows boxes in rendered output

COLS = 55
ROWS = 25


class EvidenceRenderer:

    def __init__(self, project, letterhead):
        self.project = project
        self.letterhead = letterhead

        self.evidence_html = get_template('document/evidence.html')
        self.evidence_html_static = get_template('document/evidence_static_test.html')

    @property
    def pdf(self):
        return PDFStreamer(
            HTMLParser(self.generate, CSS(self.css)),
            os.path.join(settings.MEDIA_ROOT, self.letterhead.letterhead_pdf.name),
            'landscape'
        )

    @property
    def html(self):
        return ''.join(chain(
            ('<style>', self.css, '</style>'),
            self.generate()
        ))

    @property
    def css(self):
        return render_to_string('document/evidence.css', {
            'letterhead': self.letterhead
        })

    # def generate(self):
    #     context = dict()
    #     yield self.evidence_html_static.render()

    def generate(self):
        project_data = {
            'project_pk': str(self.project.id),
            'code': "",
            'name': self.project.name,
            'id': self.project.id,
            'jobs': [],
        }

        def get_task_recursive(parent):
            if isinstance(parent, Project):
                for job in parent.jobs.all():
                    yield from get_task_recursive(job)
            else:
                for group in parent.groups.all():
                    yield from get_task_recursive(group)
                for task in parent.tasks.all():
                    # import pdb; pdb.set_trace()
                    yield {'task': {'name':task.name, 'code': task.code}}
        
        for task in get_task_recursive(self.project):
            yield self.evidence_html.render(task)


#     def generate(self):
#         for context in get_evidence_context(self.project):
#             yield self.evidence_html.render(context)
#
#
# def get_evidence_context(project):
#
#     context = {
#         'document': {
#             'date': date_format(date.today(), use_l10n=True),
#             'row_range': range(ROWS),
#             'col_range': range(COLS),
#         },
#         'project': {
#             'name': project.name,
#             'pk': project.pk,
#         }
#     }
#     for job in project.jobs.all():
#         context['job'] =  {
#             'name': job.name
#         }
#         yield from _serialize(context, job)
#
#
# def _serialize(data, parent):
#
#     for group in parent.groups.all():
#         data['group'] = {
#             'name': group.name,
#             'code': group.code,
#         }
#         yield from _serialize(group_dict, group)
#
#     for task in parent.tasks.all():
#
#         context = {
#             'task': {
#                 'code': task.code,
#                 'name': task.name,
#                 'description': task.description,
#                 'qty': task.qty,
#                 'unit': task.unit,
#             }
#         }
#         yield context

#        for lineitem in task.lineitems.all():
#            lineitem_dict = {
#                'lineitem.id': lineitem.id,
#                'name': lineitem.name,
#                'qty': lineitem.qty,
#                'unit': lineitem.unit,
#                'price': lineitem.price,
#                'estimate': lineitem.total,
#            }
#            task_dict['lineitems'].append(lineitem_dict)


# def bla_get_evidence_context(project):
#     depth = project.structure_depth
#     context = {
#         'document': {
#             'date': date_format(date.today(), use_l10n=True),
#             'row_range': range(ROWS),
#             'col_range': range(COLS),
#         },
#         'project': {
#             'name': project.name,
#             'pk': project.pk,
#         }
#     }
#     if depth == 0:
#         pass
#     elif depth == 1:
#         from django.db import connection
#         for job in project.jobs.all():
#             context['job'] = {
#                 'name': job.name,
#             }
#             for group in job.groups.all():
#                 context['group'] = {
#                     'code': group.code,
#                     'name': group.name,
#                 }
#                 for task in group.tasks.all():
#                     context['task'] = {
#                         'code': task.code,
#                         'name': task.name,
#                         'description': task.description,
#                         'qty': task.qty,
#                         'unit': task.unit,
#                     }
#                     print(f'query count: {len(connection.queries)}')
#                     yield context
#     elif depth == 2:
#         pass
#     elif depth == 3:
#         pass
#     elif depth == 4:
#         pass
#     else:
#         pass  # render error context

# ###
# # old code
# ###


# def render(project, letterhead):
#     with BytesIO() as buffer:
#         font = FontManager(letterhead.font)

#         available_width, available_height, pagesize = get_available_width_height_and_pagesize(letterhead)

#         proposal_date = date_format(date.today(), use_l10n=True)

#         doc = SystoriDocument(buffer, pagesize=pagesize, debug=DEBUG_DOCUMENT)

#         pages = []

#         render_evidence_pages(project, pages, font, proposal_date)

#         if not pages:
#             pages.append(b(_('There are no billable Tasks available.'), font))

#         doc.build(pages, LetterheadCanvas.factory(letterhead), letterhead)

#         return buffer.getvalue()


# def render_evidence_pages(project, pages, font, proposal_date):
#     project_data = {
#         'project_pk': str(project.id),
#         'code': "",
#         'name': project.name,
#         'id': project.id,
#         'jobs': [],
#     }
#     if isinstance(project, Project):
#         for job in project.jobs.all():
#             job_instance = {
#                 'code': job.code,
#                 'name': job.name,
#                 'groups': [],
#                 'tasks': [],
#             }
#             project_data['jobs'].append(job_instance)

#             _serialize_project(project_data, job_instance, job, pages, font, proposal_date)

#     if isinstance(project, Job):
#         project_data["project_pk"] = str(project.project.id)
#         job_instance = {
#             'code': project.code,
#             'name': project.name,
#             'groups': [],
#             'tasks': [],
#         }
#         project_data['jobs'].append(job_instance)

#         _serialize_project(project_data, job_instance, project, pages, font, proposal_date)

#     return None


# def _serialize_project(project_data, data, parent, pages, font, proposal_date):
#     for group in parent.groups.all():
#         group_dict = {
#             'code': group.code,
#             'name': group.name,
#             'tasks': [],
#             'groups': [],
#         }
#         data['groups'].append(group_dict)

#         _serialize_project(project_data, group_dict, group, pages, font, proposal_date)

#     for task in parent.tasks.all():
#         task_description = " / ".join([project_data['code'] + " " + project_data['name'],
#                                        data['code'] + " " + data['name']])[:110]

#         pages.append(Table([
#             [b(_('Evidence Sheet'), font), br(_('Sheet-No') + ':', font), nr('...............', font)]
#         ],
#             colWidths=[None, 50 * mm, 35 * mm]))

#         pages.append(Table([
#             [p(task_description, font), br(' #%s' % project_data['project_pk'], font), nr(proposal_date, font)],
#         ],
#             colWidths=[None, 20 * mm, 35 * mm],
#             style=[
#                 ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
#             ]
#         ))

#         pages.append(Table([
#             [b(_('Task'), font), p(task.code.strip() + ' ' + task.name[:60].strip(), font),
#              br(_('P-Amount'), font), nr('%s %s' % (ubrdecimal(task.qty).strip(), task.unit.strip()), font)]
#         ],
#             colWidths=[20 * mm, None, 35 * mm, 35 * mm],
#             style=[
#             ]
#         ))

#         t = Table([[''] * COLS] * ROWS, colWidths=[5 * mm] * COLS, rowHeights=[5 * mm] * ROWS)
#         t.setStyle(TableStyle([
#             ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey)
#         ]))
#         pages.append(t)

#         pages.append(PageBreak())
