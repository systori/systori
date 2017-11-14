from lxml import objectify

from django.forms import Form
from django.utils.translation import ugettext_lazy as _

from systori.apps.task.models import Job, Group, Task
from systori.apps.project.models import Project
from systori.apps.accounting.models import create_account_for_job


"""
 <GAEB xmlns="http://www.gaeb.de/GAEB_DA_XML/200407">
 <GAEB xmlns="http://www.gaeb.de/GAEB_DA_XML/DA83/3.2">
"""


class Export:

    NAMESPACE = "http://www.gaeb.de/GAEB_DA_XML/200407"

    def __init__(self):
        self.e = objectify.ElementMaker(
            annotate=False,
            namespace=self.NAMESPACE,
            nsmap={None: self.NAMESPACE}
        )

    def project(self, project, jobs=None):
        jobs = jobs if jobs is not None else list(project.jobs.all())
        return self.e.GAEB(
            self.e.PrjInfo(
                self.e.LblPrj(project.name)
            ),
            self.e.Award(
                self.e.BoQ(
                    self.e.BoQInfo(*(
                        self.e.BoQBkdn(
                            self.e.Type('BoQLevel'),
                            self.e.Length(fill),
                            self.e.Num('Yes'),
                        ) for fill in project.structure.zfill[:-1]),
                        self.e.BoQBkdn(
                            self.e.Type('Item'),
                            self.e.Length(project.structure.zfill[-1]),
                            self.e.Num('Yes'),
                        )
                    ),
                    self.e.BoQBody(
                        *(self.group(job) for job in jobs)
                    )
                )
            )
        )

    def group(self, group):
        body = [self.group(g) for g in group.groups.all()]
        tasks = [self.task(g) for g in group.tasks.all()]
        if tasks:
            body.append(self.e.Itemlist(*tasks))
        return self.e.BoQCtgy(
            self.e.LblTx(group.name),
            self.e.BoQBody(*body)
        )

    def task(self, task):
        elements = [
            self.e.Qty(task.qty),
            self.e.QU(task.unit),
            self.e.Description(
                self.e.CompleteText(
                    self.e.OutlineText(
                        self.e.OutlTxt(
                            self.e.TextOutlTxt(task.name)
                        )
                    ),
                    self.e.DetailTxt(
                        self.e.Text(task.description)
                    )
                )
            )
        ]
        if task.is_provisional:
            elements.append(self.e.Provis())
        if task.variant_group > 0:
            elements.append(self.e.ALNGroupNo(task.variant_group))
            elements.append(self.e.ALNSerNo(task.variant_serial))
        return self.e.Item(*elements)


def get(el, path, default=None, required=False, element_only=False):
    parts = path.split('.')
    if hasattr(el, parts[0]):
        el = getattr(el, parts[0])
        if len(parts) > 1:
            return get(el, '.'.join(parts[1:]), default, required, element_only)
        else:
            if element_only:
                return el
            else:
                return el.pyval
    else:
        return default


class Import:

    def __init__(self, project, form=None):
        self.project = project
        self.form = form if form is not None else Form({})
        self.objects = []
        self.jobs = []
        self.max_group_depth = 0
        self.ns = None

    def save(self):
        for object in self.objects:
            object.refresh_pks()
            object.save()
        for job in self.jobs:
            job.account = create_account_for_job(job)
            job.save()
        return self.jobs

    def error(self, msg, line=None):
        if not self.form:
            return
        if line:
            self.form.add_error(None, '{} Line: {}'.format(msg, line))
        else:
            self.form.add_error(None, msg)

    def parse(self, file):
        try:
            tree = objectify.parse(file)
            self.ns = '{' + tree.xpath('namespace-uri(.)') + '}'
            root = tree.getroot()
            if not self.project.name:
                self.project.name = root.PrjInfo.LblPrj
                self.parse_structure(root)
            for job_element in root.Award.BoQ.BoQBody.iterchildren(self.ns+'BoQCtgy'):
                self.group(self.project, job_element)
            if self.project.structure.maximum_depth != self.max_group_depth:
                self.error(_("Project and imported jobs do not have compatible structure."))
        except:
            self.error(_("File '%s' can't be imported. Please contact support.") % file.name)
        return self

    def parse_structure(self, root):
        parts = []
        for part in root.Award.BoQ.BoQInfo.iterchildren(self.ns+'BoQBkdn'):
            pad = int(part.Length)
            is_number = part.Num == 'Yes'
            if part.Type in ('BoQLevel', 'Item'):
                parts.append('1'.zfill(pad))
        self.project.structure = '.'.join(parts)

    def group(self, parent, group_element):
        try:
            if isinstance(parent, Project):
                group = Job(name=" ".join(group_element.LblTx.xpath(".//text()")), project=parent)
                group.job = group
                self.jobs.append(group)
            else:
                group = Group(name=" ".join(group_element.LblTx.xpath(".//text()")), parent=parent)
            self.max_group_depth = max(self.max_group_depth, group.depth)
            self.objects.append(group)
            for sub_group_element in group_element.BoQBody.iterchildren(self.ns+'BoQCtgy'):
                self.group(group, sub_group_element)
            if hasattr(group_element.BoQBody, 'Itemlist'):
                for task_element in group_element.BoQBody.Itemlist.iterchildren(self.ns+'Item'):
                    self.task(group, task_element)
        except:
            self.error(_('Error processing group.'), group_element.sourceline)

    def task(self, group, task_element):
        try:
            task = Task(group=group)
            self.objects.append(task)
            task.qty = get(task_element, "Qty", default=0)
            task.unit = get(task_element, "QU", default="INFO")
            for text_node in task_element.Description.CompleteText.DetailTxt.getchildren():
                for p in text_node.getchildren():
                    for child in p.getchildren():
                        if child.tag == self.ns+"span":
                            task.description += " ".join(child.xpath(".//text()"))
                        elif child.tag == self.ns+"image":
                            task.description += str(_(" Info: Picture was in Imported File."))
            for text_node in task_element.Description.CompleteText.OutlineText.getchildren():
                task.name = " ".join(text_node.xpath(".//text()"))
        except:
            self.error(_('Error processing task.'), task_element.sourceline)
