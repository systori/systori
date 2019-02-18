import os
from itertools import chain
from datetime import date

from django.utils.formats import date_format
from django.conf import settings
from django.template.loader import get_template, render_to_string

from systori.apps.project.models import Project
from systori.apps.task.models import Job, Group, Task

from bericht.pdf import PDFStreamer
from bericht.html import HTMLParser, CSS

DEBUG_DOCUMENT = False  # Shows boxes in rendered output

COLS = 55
ROWS = 25


class EvidenceRenderer:
    def __init__(self, project, letterhead):
        self.project = project
        self.letterhead = letterhead

        self.evidence_html = get_template("document/evidence.html")

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
            "document/evidence.css", {"letterhead": self.letterhead}
        )

    def generate(self):
        def get_project_meta_from_model():
            if isinstance(self.project, Project):
                return (str(self.project.id), self.project.name)
            elif isinstance(self.project, Job):
                return (str(self.project.project.id), self.project.project.name)

        project_data = {
            "pk": get_project_meta_from_model()[0],
            "name": get_project_meta_from_model()[1],
        }
        document_date = date_format(date.today(), use_l10n=True)

        def get_task_recursive(parent):
            if isinstance(parent, Project):
                for job in parent.jobs.all():
                    yield from get_task_recursive(job)
            else:
                for group in parent.groups.all():
                    yield from get_task_recursive(group)
                for task in (
                    parent.tasks.prefetch_related("group").prefetch_related("job").all()
                ):
                    yield {
                        "document": {"date": document_date},
                        "project": {
                            "pk": project_data["pk"],
                            "name": project_data["name"],
                        },
                        "job": {"name": task.job.name},
                        "group": {"name": task.group.name},
                        "task": {
                            "name": task.name,
                            "code": task.code,
                            "qty": task.qty,
                            "unit": task.unit,
                        },
                    }

        for task in get_task_recursive(self.project):
            yield self.evidence_html.render(task)
