from decimal import Decimal
from django.db import models, connections
from django.db.models.manager import BaseManager
from ordered_model.models import OrderedModel
from django.utils.translation import ugettext_lazy as _
from django_fsm import FSMField, transition
from django.utils.functional import cached_property


class BetterOrderedModel(OrderedModel):

    class Meta(OrderedModel.Meta):
        abstract = True

    def save(self, *args, **kwargs):
        if not self.pk and self.order != None:
            qs = self.get_ordering_queryset()
            qs.filter(order__gte=self.order).update(order=models.F('order') + 1)
        super(BetterOrderedModel, self).save(*args, **kwargs)


TAX_RATE = Decimal(.19)

class JobQuerySet(models.QuerySet):

    def estimate_total(self):
        return sum([job.estimate_total for job in self.all()])

    def estimate_tax_total(self):
        return self.estimate_total() * TAX_RATE

    def estimate_gross_total(self):
        return self.estimate_total() * (TAX_RATE+1)

    def billable_total(self):
        return sum([job.billable_total for job in self.all()])

    def billable_tax_total(self):
        return self.billable_total() * TAX_RATE

    def billable_gross_total(self):
        return self.billable_total() * (TAX_RATE+1)

class JobManager(BaseManager.from_queryset(JobQuerySet)):
    use_for_related_fields = True


class Job(BetterOrderedModel):

    name = models.CharField(_('Job Name'), max_length=512)
    description = models.TextField(_('Description'), blank=True)

    FIXED_PRICE = "fixed_price"
    TIME_AND_MATERIALS = "time_and_materials"
    BILLING_METHOD = (
        (FIXED_PRICE , _("Fixed Price")),
        (TIME_AND_MATERIALS, _("Time and Materials")),
    )
    billing_method = models.CharField(_('Billing Method'), max_length=128, choices=BILLING_METHOD, default=FIXED_PRICE)

    project = models.ForeignKey('project.Project', related_name="jobs")
    order_with_respect_to = 'project'

    DRAFT = "draft"
    PROPOSED = "proposed"
    APPROVED = "approved"
    STARTED = "started"
    COMPLETED = "completed"

    STATE_CHOICES = (
        (DRAFT, _("Draft")),
        (PROPOSED, _("Proposed")),
        (APPROVED, _("Approved")),
        (STARTED, _("Started")),
        (COMPLETED, _("Completed"))
    )

    status = FSMField(default=DRAFT, choices=STATE_CHOICES)

    objects = JobManager()

    class Meta(OrderedModel.Meta):
        verbose_name = _("Job")
        verbose_name_plural = _("Job")

    @transition(field=status, source=[APPROVED,COMPLETED], target=STARTED, custom={'label': _("Start")})
    def start(self):
        pass

    @transition(field=status, source=STARTED, target=COMPLETED, custom={'label': _("Complete")})
    def complete(self):
        pass

    def clone_to(self, other_job):
        taskgroups = self.taskgroups.all()
        for taskgroup in taskgroups:
            taskgroup.clone_to(other_job, taskgroup.order)

    def _total_calc(self, calc_type):
        field = "{}_{}".format(self.billing_method, calc_type)
        total = Decimal(0.0)
        for taskgroup in self.taskgroups.all():
            total += getattr(taskgroup, field)
        return total

    @property
    def estimate_total(self):
        return self._total_calc('estimate')

    @property
    def billable_total(self):
        return self._total_calc('billable')

    @property
    def code(self):
        return str(self.order+1).zfill(self.project.job_zfill)

    def __str__(self):
        return '{} {}'.format(self.code, self.name)

class TaskGroup(BetterOrderedModel):

    name = models.CharField(_("Name"), max_length=512)
    description = models.TextField(blank=True)

    job = models.ForeignKey(Job, related_name="taskgroups")
    order_with_respect_to = 'job'

    class Meta(OrderedModel.Meta):
        verbose_name = _("Task Group")
        verbose_name_plural = _("Task Groups")

    def _total_calc(self, field):
        total = Decimal(0.0)
        for task in self.tasks.all():
            total += getattr(task, field)
        return total

    @property
    def fixed_price_estimate(self):
        return self._total_calc('fixed_price_estimate')

    @property
    def fixed_price_billable(self):
        return self._total_calc('fixed_price_billable')

    @property
    def time_and_materials_estimate(self):
        return self._total_calc('time_and_materials_estimate')

    @property
    def time_and_materials_billable(self):
        return self._total_calc('time_and_materials_billable')

    @property
    def estimate_total(self):
        return self.fixed_price_estimate

    @property
    def billable_total(self):
        return self.fixed_price_billable

    @property
    def code(self):
        parent_code = self.job.code
        self_code = str(self.order+1).zfill(self.job.project.taskgroup_zfill)
        return '{}.{}'.format(parent_code, self_code)

    def __str__(self):
        return '{} {}'.format(self.code, self.name)

    def clone_to(self, new_job, new_order):
        tasks = self.tasks.all()
        self.pk = None
        self.job = new_job
        self.order = new_order
        self.save()
        for task in tasks:
            task.clone_to(self, task.order)


class Task(BetterOrderedModel):
    name = models.CharField(_("Name"), max_length=512)
    description = models.TextField()

    taskgroup = models.ForeignKey(TaskGroup, related_name="tasks")
    order_with_respect_to = 'taskgroup'

    class Meta(OrderedModel.Meta):
        verbose_name = _("Task")
        verbose_name_plural = _("Task")

    @cached_property
    def instance(self):
        return self.taskinstances.all()[0]

    @property
    def unit_price(self):
        return self.instance.unit_price

    @property
    def fixed_price_estimate(self):
        return self.instance.fixed_price_estimate

    @property
    def fixed_price_billable(self):
        return self.instance.fixed_price_billable

    @property
    def time_and_materials_estimate(self):
        return self.instance.time_and_materials_estimate

    @property
    def time_and_materials_billable(self):
        return self.instance.time_and_materials_billable

    @property
    def code(self):
        parent_code = self.taskgroup.code
        self_code = str(self.order+1).zfill(self.taskgroup.job.project.task_zfill)
        return '{}.{}'.format(parent_code, self_code)

    def __str__(self):
        return '{} {}'.format(self.code, self.name)

    def clone_to(self, new_taskgroup, new_order):
        taskinstances = self.taskinstances.all()
        self.pk = None
        self.taskgroup = new_taskgroup
        self.order = new_order
        self.save()
        for taskinstance in taskinstances:
            taskinstance.clone_to(self, taskinstance.order)


class TaskInstance(BetterOrderedModel):
    """
    A TaskInstance is a concrete version of a task that can actually be executed.
    For example, a Task could be to "Install a window."
    This task could have two TaskInstances:
      1. Install a standard window.
      2. Install an insulated window.
    A single TaskInstance must be chosen (by customer) before a Task can be invoiced or tracked.
    """

    name = models.CharField(_("Name"), max_length=512)
    description = models.TextField()

    # tracking completion of this task by a quantifiable indicator, an estimate
    qty = models.DecimalField(_("Quantity"), max_digits=12, decimal_places=2)

    # unit for the completion tracking quantifiable indicator
    unit = models.CharField(_("Unit"), max_length=64)

    # how much of the project is complete in units of quantity
    # may be more than qty
    complete = models.DecimalField(_("Complete"), max_digits=12, decimal_places=2, default=0.0)

    # date when this task was started
    started_on = models.DateField(blank=True, null=True)

    # date when complete became equal to qty
    completed_on = models.DateField(blank=True, null=True)

    task = models.ForeignKey(Task, related_name="taskinstances")
    order_with_respect_to = 'task'

    class Meta(OrderedModel.Meta):
        verbose_name = _("Task Instance")
        verbose_name_plural = _("Task Instances")

    # For fixed price billing, returns the price
    # per unit of this task
    @property
    def unit_price(self):
        t = Decimal(0.0)
        for lineitem in self.lineitems.all():
            t += lineitem.price_per_task_unit
        return t

    # For fixed price billing, returns the estimated price
    # to complete this task.
    @property
    def fixed_price_estimate(self):
        return self.unit_price * self.qty

    # For fixed price billing, returns the price based
    # on what has been completed.
    @property
    def fixed_price_billable(self):
        return self.unit_price * self.complete

    # For time and materials billing, returns
    # the estimated amount that will been expended by
    # all line items contained by this task.
    @property
    def time_and_materials_estimate(self):
        t = Decimal(0.0)
        for lineitem in self.lineitems.all():
            t += lineitem.time_and_materials_estimate
        return t

    # For time and materials billing, returns
    # the total amount that has been expended by
    # all line items contained by this task.
    @property
    def time_and_materials_billable(self):
        t = Decimal(0.0)
        for lineitem in self.lineitems.all():
            t += lineitem.time_and_materials_billable
        return t

    @property
    def code(self):
        parent_code = self.taskgroup.code
        self_code = str(self.order+1).zfill(self.taskgroup.job.project.task_zfill)
        return '{}.{}'.format(parent_code, self_code)

    def __str__(self):
        return '{} {}'.format(self.code, self.name)

    def clone_to(self, new_task, new_order):
        lineitems = self.lineitems.all()
        self.pk = None
        self.task = new_task
        self.order = new_order
        self.save()
        for lineitem in lineitems:
            lineitem.pk = None
            lineitem.taskoption = self
            lineitem.save()


class LineItem(models.Model):

    name = models.CharField(_("Name"), max_length=512)

    # fixed billing, amount of hours or materials to complete just one unit of the task
    unit_qty = models.DecimalField(_("Quantity"), max_digits=12, decimal_places=2, default=0.0)

    # time and materials billing, amount of hours or materials to complete the entire task
    task_qty = models.DecimalField(_("Quantity"), max_digits=12, decimal_places=2, default=0.0)

    # time and materials billing, how many units of this have been delivered/expended and can thus be billed
    billable = models.DecimalField(_("Billable"), max_digits=12, decimal_places=2, default=0.0)

    # unit for the quantity
    unit = models.CharField(_("Unit"), max_length=64)

    # price per unit
    price = models.DecimalField(_("Price"), max_digits=12, decimal_places=2)

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

    taskinstance = models.ForeignKey(TaskInstance, related_name="lineitems")

    class Meta:
        verbose_name = _("Line Item")
        verbose_name_plural = _("Line Items")
        ordering = ['id']

    # For fixed price billing, returns the price
    # of this line item per 1 unit of the parent task.
    @property
    def price_per_task_unit(self):
        return self.price * self.unit_qty

    # For time and materials billing, returns the estimated price
    # of this line item to complete the entire task.
    @property
    def time_and_materials_estimate(self):
        return self.price * self.task_qty

    # For time and materials billing, returns
    # the total amount that has been expended.
    @property
    def time_and_materials_billable(self):
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