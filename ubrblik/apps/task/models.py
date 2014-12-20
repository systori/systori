from django.db import models, connections
from ordered_model.models import OrderedModel
from django.utils.translation import ugettext_lazy as _


class Job(OrderedModel):

    name = models.CharField(_('Job Name'), max_length=128)
    description = models.TextField()

    project = models.ForeignKey('project.Project', related_name="jobs")
    order_with_respect_to = 'project'

    class Meta(OrderedModel.Meta):
        verbose_name = _("Job")
        verbose_name_plural = _("Job")

    @property
    def total(self):
        t = 0
        for group in self.taskgroups.all():
            t += group.total
        return t


class TaskGroup(OrderedModel):

    name = models.CharField(_("Name"), max_length=128)
    description = models.TextField()

    job = models.ForeignKey(Job, related_name="taskgroups")
    order_with_respect_to = 'job'

    class Meta(OrderedModel.Meta):
        verbose_name = _("Task Group")
        verbose_name_plural = _("Task Groups")

    @property
    def code(self):
        return self.id

    @property
    def total(self):
        t = 0
        for task in self.tasks.all():
            t += task.total
        return t


class Task(OrderedModel):

    name = models.CharField(_("Name"), max_length=128)
    description = models.TextField()

    # not null value here means this task needs attention
    # date is helpful to know when it was marked for attention
    # see progress reports for details on what needs attention
    needs_attention = models.DateField(blank=True, null=True)

    # date when this task was started
    started_on = models.DateField(blank=True, null=True)

    # date when this task became ready for invoicing
    completed_on = models.DateField(blank=True, null=True)

    # document where this task is invoiced
    invoice =  models.ForeignKey("document.Document", related_name="tasks", blank=True, null=True, on_delete=models.SET_NULL)

    # copy of last not null ProgressReport.progress integer
    progress = models.PositiveSmallIntegerField(default=0)

    # points to the last progress report that was created
    # TODO: on_delete should set this to the next most recent progress report
    progress_report = models.ForeignKey('ProgressReport', related_name='+', blank=True, null=True, on_delete=models.SET_NULL)

    taskgroup = models.ForeignKey(TaskGroup, related_name="tasks")
    order_with_respect_to = 'taskgroup'

    class Meta(OrderedModel.Meta):
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")

    @property
    def code(self):
        return "{}.{}".format(self.taskgroup_id, self.id)

    @property
    def total(self):
        t = 0
        for lineitem in self.lineitems.all():
            t += lineitem.total
        return t


# progress report serves multiple purposes:
#  1. general comments
#  2. quantifiable progress (1..100)
#  3. evidence of completion documents (see document.ProgressAttachment)
class ProgressReport(models.Model):
    date = models.DateField(auto_now_add=True)
    comment = models.TextField()
    progress = models.PositiveSmallIntegerField()

    task = models.ForeignKey(Task, related_name="reports")

    class Meta:
        verbose_name = _("Progress Report")
        verbose_name_plural = _("Progress Reports")


class LineItem(OrderedModel):

    name = models.CharField(_("Name"), max_length=128)
    qty = models.DecimalField(_("Quantity"), max_digits=12, decimal_places=2)
    unit = models.CharField(_("Unit"), max_length=64)
    price = models.DecimalField(_("Price"), max_digits=12, decimal_places=2)

    task = models.ForeignKey(Task, related_name="lineitems")
    order_with_respect_to = 'task'

    class Meta(OrderedModel.Meta):
        verbose_name = _("Line Item")
        verbose_name_plural = _("Line Items")

    @property
    def total(self):
        return self.price * self.qty