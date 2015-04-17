from lxml import objectify, etree

from ..task.models import Job, TaskGroup, Task, TaskInstance
from .models import Project

def get_text(element):
    concatenated = []
    print("-------------------------------------------")
    for idx, el in enumerate(element.getchildren()):
        print(el.tag)
        print(idx)
        if el.tag is el.getparent().Text:
            print("el.Text")
        #elif el.tag is el.getparent().TextComplement:
        #   print("el.Compl")
        else:
            print("hallo")


def item_info(item):
    print("item_info called")
    name = item.Description.CompleteText.OutlineText.OutlTxt.TextOutlTxt.p.span.text
    description = [get_text(el) for el in item.Description.CompleteText.DetailTxt]
    return name, description

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

def gaeb_import(filepath):
        tree = objectify.parse(filepath)
        root = tree.getroot()
        label = root.PrjInfo.LblPrj
        project = Project.objects.create(name=label)
        for ctgy in root.Award.BoQ.BoQBody.BoQCtgy:
            job = Job.objects.create(name=" ".join(ctgy.LblTx.xpath(".//text()")), project=project)
            for grp in ctgy.BoQBody.BoQCtgy:
                taskgroup = TaskGroup.objects.create(name=" ".join(grp.LblTx.xpath(".//text()")), job=job)
                for item in grp.BoQBody.Itemlist.getchildren():
                    task = Task.objects.create(taskgroup=taskgroup)
                    task.qty = item.Qty.text
                    task.unit = item.QU.text
                    for text_node in item.Description.CompleteText.DetailTxt.getchildren():
                        task.description = " ".join(text_node.xpath(".//text()"))
                    for text_node in item.Description.CompleteText.OutlineText.getchildren():
                        task.name = " ".join(text_node.xpath(".//text()"))
                    TaskInstance.objects.create(task=task, selected=True)
                    task.save()
                taskgroup.save()
            job.save()
        return project.id

