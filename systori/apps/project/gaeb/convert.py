from lxml import etree, objectify

from django.forms import Form
from django.utils.translation import ugettext_lazy as _

from systori.apps.task.models import Job, Group, Task
from systori.apps.accounting.models import Account
from systori.apps.project.models import Project, JobSite


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

    def __init__(self, form=None, project=None):
        self.form = form if form is not None else Form({})
        self.project = project
        self.objects = []
        self.ns = None

    def save(self):
        project = self.project
        if not project.pk:
            project.save()
            project.account = Account.objects.create(account_type=Account.ASSET, code=str(10000 + project.id))
            JobSite.objects.create(
                project=project, name=_('Main Site'),
                #address="", city="",
                #postal_code=""
            )
        for object in self.objects:
            object.refresh_pks()
            object.save()
        return project

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
            if self.project is None:
                self.project = Project(name=root.PrjInfo.LblPrj)
            for job_element in root.Award.BoQ.BoQBody.iterchildren(self.ns+'BoQCtgy'):
                self.group(self.project, job_element)
        except:
            self.error(_("File '%s' can't be imported. Please contact support.") % file.name)
        return self

    def group(self, parent, group_element):
        try:
            if isinstance(parent, Project):
                group = Job(name=" ".join(group_element.LblTx.xpath(".//text()")), project=parent)
                group.job = group
            else:
                group = Group(name=" ".join(group_element.LblTx.xpath(".//text()")), parent=parent)
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
