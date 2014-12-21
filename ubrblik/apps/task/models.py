from django.db import models, connections
from ordered_model.models import OrderedModel
from django.utils.translation import ugettext_lazy as _


class Job(OrderedModel):

    name = models.CharField(_('Job Name'), max_length=512)
    description = models.TextField()

    project = models.ForeignKey('project.Project', related_name="jobs")
    order_with_respect_to = 'project'

    class Meta(OrderedModel.Meta):
        verbose_name = _("Job")
        verbose_name_plural = _("Job")

    @property
    def total_amount(self):
        t = 0
        for taskgroup in self.taskgroups.all():
            t += taskgroup.total_amount
        return t

    @property
    def billable_amount(self):
        t = 0
        for taskgroup in self.taskgroups.all():
            t += taskgroup.billable_amount
        return t


class TaskGroup(OrderedModel):

    name = models.CharField(_("Name"), max_length=512)
    description = models.TextField()

    job = models.ForeignKey(Job, related_name="taskgroups")
    order_with_respect_to = 'job'

    class Meta(OrderedModel.Meta):
        verbose_name = _("Task Group")
        verbose_name_plural = _("Task Groups")

    @property
    def total_amount(self):
        t = 0
        for task in self.tasks.all():
            t += task.total_amount
        return t

    @property
    def billable_amount(self):
        t = 0
        for task in self.tasks.all():
            t += task.billable_amount
        return t


class Task(OrderedModel):

    name = models.CharField(_("Name"), max_length=512)
    description = models.TextField()

    # tracking completion of this task by a quantifiable indicator
    qty = models.DecimalField(_("Quantity"), max_digits=12, decimal_places=2)

    # unit for the completion tracking quantifiable indicator
    unit = models.CharField(_("Unit"), max_length=64)

    # how much of the project is complete in units of quantity
    complete = models.DecimalField(_("Complete"), max_digits=12, decimal_places=2, default=0.0)

    # date when this task was started
    started_on = models.DateField(blank=True, null=True)

    # date when complete became equal to qty
    completed_on = models.DateField(blank=True, null=True)

    taskgroup = models.ForeignKey(TaskGroup, related_name="tasks")
    order_with_respect_to = 'taskgroup'

    class Meta(OrderedModel.Meta):
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")

    @property
    def total_amount(self):
        t = 0
        for lineitem in self.lineitems.all():
            t += lineitem.total_amount
        return t

    @property
    def billable_amount(self):
        t = 0
        for lineitem in self.lineitems.all():
            t += lineitem.billable_amount
        return t


class LineItem(models.Model):

    name = models.CharField(_("Name"), max_length=512)

    # amount of hours or materials
    qty = models.DecimalField(_("Quantity"), max_digits=12, decimal_places=2)

    # unit for the quantity
    unit = models.CharField(_("Unit"), max_length=64)

    # price per unit
    price = models.DecimalField(_("Price"), max_digits=12, decimal_places=2)

    # how many units of this have been delivered/expended and can be thus be billed
    billable = models.DecimalField(_("Billable"), max_digits=12, decimal_places=2, default=0.0)

    # when labor is true, this will cause this line item to show up in time sheet and other
    # labor related parts of the system
    is_labor = models.BooleanField(default=False)
    
    # when material is true, this will cause this line item to show up in materials tracking
    # and other inventory parts of the system
    is_material = models.BooleanField(default=False)

    # flagged items will appear in the project dashboard as needing attention
    # could be set automatically by the system from temporal triggers (materials should have been delivered by now)
    # or it could be set manual by a users
    is_flagged = models.BooleanField(default=False)

    task = models.ForeignKey(Task, related_name="lineitems")

    class Meta:
        verbose_name = _("Line Item")
        verbose_name_plural = _("Line Items")
        ordering = ['id']

    @property
    def total_amount(self):
        return self.price * self.qty

    @property
    def billable_amount(self):
        return self.price * self.billable


class ProgressReport(models.Model):

    # date when this progress report was filed
    date = models.DateField(auto_now_add=True)

    # description of what has been done
    comment = models.TextField()

    # how much of the project is complete in units of quantity
    # this gets copied into task.complete with the latest progress report value
    complete = models.DecimalField(_("Complete"), max_digits=12, decimal_places=2)

    task = models.ForeignKey(Task, related_name="reports")

    class Meta:
        verbose_name = _("Progress Report")
        verbose_name_plural = _("Progress Reports")
        ordering = ['date']


class ProgressAttachment(models.Model):

    report = models.ForeignKey(ProgressReport, related_name="attachments")
    attachment = models.FileField()

    class Meta:
        verbose_name = _("Attachment")
        verbose_name_plural = _("Attachments")
        ordering = ['id']