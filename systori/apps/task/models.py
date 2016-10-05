from math import floor, ceil
from decimal import Decimal
from datetime import datetime
from string import ascii_lowercase
from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import ugettext_lazy as _
from django.utils.formats import date_format
from django_fsm import FSMField, transition
from django.utils.functional import cached_property


class JobQuerySet(models.QuerySet):
    def estimate_total(self):
        return sum([job.estimate_total for job in self])

    def progress_total(self):
        return sum([job.progress_total for job in self])


class JobManager(BaseManager.from_queryset(JobQuerySet)):
    use_for_related_fields = True


class Job(models.Model):
    name = models.CharField(_('Job Name'), max_length=512)
    job_code = models.PositiveSmallIntegerField(_('Code'), default=0)
    description = models.TextField(_('Description'), blank=True)
    project = models.ForeignKey('project.Project', related_name="jobs")

    taskgroup_offset = models.PositiveSmallIntegerField(_("Task Group Offset"), default=0)

    account = models.OneToOneField('accounting.Account', related_name="job", null=True, on_delete=models.SET_NULL)

    ESTIMATE_INCREMENT = 0.05
    ESTIMATE_INCREMENT_DISPLAY = '{:.0%}'.format(ESTIMATE_INCREMENT)

    FIXED_PRICE = "fixed_price"
    TIME_AND_MATERIALS = "time_and_materials"
    BILLING_METHOD = (
        (FIXED_PRICE, _("Fixed Price")),
        (TIME_AND_MATERIALS, _("Time and Materials")),
    )
    billing_method = models.CharField(_('Billing Method'), max_length=128, choices=BILLING_METHOD, default=FIXED_PRICE)
    is_revenue_recognized = models.BooleanField(default=False)

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

    STATUS_FOR_PROPOSAL = (DRAFT, PROPOSED)

    objects = JobManager()

    class Meta:
        verbose_name = _("Job")
        verbose_name_plural = _("Job")
        ordering = ['job_code']

    @transition(field=status, source="*", target=DRAFT)
    def draft(self):
        pass

    @transition(field=status, source=DRAFT, target=PROPOSED)
    def propose(self):
        pass

    @transition(field=status, source=[PROPOSED, DRAFT], target=APPROVED)
    def approve(self):
        pass

    @transition(field=status, source=[APPROVED, COMPLETED], target=STARTED, custom={'label': _("Start")})
    def start(self):
        pass

    @property
    def is_started(self):
        return self.status == Job.STARTED

    @transition(field=status, source=STARTED, target=COMPLETED, custom={'label': _("Complete")})
    def complete(self):
        pass

    @staticmethod
    def prefetch(job_id):
        return \
            Job.objects.filter(id=job_id) \
                .prefetch_related('taskgroups__tasks__taskinstances__lineitems') \
                .get()

    def has_level(self, level):
        if level > 5:
            return False
        return getattr(self.project, 'has_level_'+str(level))

    @cached_property
    def taskgroups(self):
        level = 3
        prefetch = []
        while self.has_level(level):
            prefetch.append('children')
            level += 1
        prefetch += ['tasks', 'taskinstances', 'lineitems']
        return list(
            self._taskgroups
                .filter(level=2)
                .prefetch_related('__'.join(prefetch))
                .all()
        )

    @property
    def code(self):
        return str(self.job_code).zfill(self.project.level_1_zfill)

    @property
    def can_propose(self):
        return self.status in self.STATUS_FOR_PROPOSAL

    @property
    def billable_taskgroups(self):
        for taskgroup in self.taskgroups.all():
            if taskgroup.is_billable:
                yield taskgroup

    @property
    def is_billable(self):
        for taskgroup in self.billable_taskgroups:
            return True
        return False

    def clone_to(self, other_job):
        for taskgroup in self.taskgroups:
            taskgroup.clone_to(other_job, taskgroup.order)

    def _total_calc(self, calc_type):
        field = "{}_{}".format(self.billing_method, calc_type)
        total = Decimal(0.0)
        for task in self.tasks.all():
            total += getattr(task, field)
        return total

    def estimate_total_modify(self, worker, action):
        for task in self.tasks.all():
            task.estimate_total_modify(worker, action, self.ESTIMATE_INCREMENT)

    @property
    def estimate_total(self):
        return self._total_calc('estimate')

    @property
    def progress_total(self):
        return self._total_calc('progress')

    @property
    def progress_percent(self):
        percent = self.progress_total / self.estimate_total * 100 if self.estimate_total else 0
        if percent < 100:
            return floor(percent)
        elif percent > 100:
            return ceil(percent)
        else:
            return 100

    def __str__(self):
        return self.name


class OrderedModel(models.Model):

    order = models.PositiveIntegerField(_('Order'), editable=False, db_index=True)
    order_with_respect_to = None

    class Meta:
        abstract = True

    def get_ordering_queryset(self):
        assert self.order_with_respect_to is not None, "Subclasses of OrderbleModel must set order_with_respect_to."
        return self.__class__.objects.filter((self.order_with_respect_to, getattr(self, self.order_with_respect_to)))

    def save(self, *args, **kwargs):
        if not self.pk and self.order is not None:
            qs = self.get_ordering_queryset()
            qs.filter(order__gte=self.order).update(order=models.F('order') + 1)
        if self.order is None:
            c = self.get_ordering_queryset().aggregate(models.Max('order')).get('order__max')
            self.order = 0 if c is None else c + 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        qs = self.get_ordering_queryset()
        qs.filter(order__gt=self.order).update(order=models.F('order')-1)
        super().delete(*args, **kwargs)

    def move_to(self, order):
        if order is None or self.order == order:
            # object is already at desired position
            return
        qs = self.get_ordering_queryset()
        if self.order > order:
            qs.filter(order__lt=self.order, order__gte=order).update(order=models.F('order')+1)
        else:
            qs.filter(order__gt=self.order, order__lte=order).update(order=models.F('order')-1)
        self.order = order
        self.save()


class TaskGroup(OrderedModel):

    name = models.CharField(_("Name"), max_length=512)
    description = models.TextField(_("Description"), blank=True)
    parent = models.ForeignKey('self', related_name='children', null=True, on_delete=models.CASCADE)
    level = models.PositiveIntegerField(_('Level'), editable=False)

    job = models.ForeignKey(Job, related_name="_taskgroups")

    order_with_respect_to = 'parent'

    class Meta:
        verbose_name = _("Task Group")
        verbose_name_plural = _("Task Groups")
        ordering = ('order',)

    def generate_children(self):
        if self.job.has_level(self.level+1):
            child = TaskGroup.objects.create(
                name="",
                description="",
                parent=self,
                job=self.job,
                level=self.level+1
            )
            child.generate_children()

    def clone_to(self, new_job, new_order):
        tasks = self.tasks.all()
        self.pk = None
        self.job = new_job
        self.order = new_order
        self.save()
        for task in tasks:
            task.clone_to(self, task.order)

    @property
    def billable_tasks(self):
        for task in self.tasks.all():
            if task.is_billable:
                yield task

    @property
    def is_billable(self):
        for task in self.billable_tasks:
            return True
        return False

    def _total_calc(self, field, include_optional=True):
        total = Decimal(0.0)
        for task in self.tasks.all():
            if include_optional or not task.is_optional:
                total += getattr(task, field)
        return total

    @property
    def fixed_price_estimate(self):
        return self._total_calc('fixed_price_estimate', include_optional=False)

    @property
    def fixed_price_progress(self):
        return self._total_calc('fixed_price_progress')

    @property
    def time_and_materials_estimate(self):
        return self._total_calc('time_and_materials_estimate', include_optional=False)

    @property
    def time_and_materials_progress(self):
        return self._total_calc('time_and_materials_progress')

    @property
    def estimate_total(self):
        return self.fixed_price_estimate

    @property
    def progress_total(self):
        return self.fixed_price_progress

    @property
    def code(self):
        parent_code = self.job.code
        offset = self.job.taskgroup_offset
        self_code = str(self.order + 1 + offset).zfill(self.job.project.level_2_zfill)
        return '{}.{}'.format(parent_code, self_code)

    def __str__(self):
        return '{} {}'.format(self.code, self.name)


class Task(OrderedModel):
    name = models.CharField(_("Name"), max_length=512)
    description = models.TextField()

    # tracking completion of this task by a quantifiable indicator, an estimate
    qty = models.DecimalField(_("Quantity"), max_digits=14, decimal_places=4, default=0.0)

    # unit for the completion tracking quantifiable indicator
    unit = models.CharField(_("Unit"), max_length=64)

    # how much of the project is complete in units of quantity
    # may be more than qty
    complete = models.DecimalField(_("Complete"), max_digits=14, decimal_places=4, default=0.0)

    # tasks marked optional aren't included in the total
    is_optional = models.BooleanField(default=False)

    started_on = models.DateField(blank=True, null=True)
    completed_on = models.DateField(blank=True, null=True)

    job = models.ForeignKey(Job, related_name="tasks", null=True)
    taskgroup = models.ForeignKey(TaskGroup, related_name="tasks")
    order_with_respect_to = 'taskgroup'

    APPROVED = "approved"
    READY = "ready"
    RUNNING = "running"
    DONE = "done"

    STATE_CHOICES = (
        (APPROVED, _("Approved")),
        (READY, _("Ready")),
        (RUNNING, _("Running")),
        (DONE, _("Done"))
    )

    status = FSMField(blank=True, choices=STATE_CHOICES)

    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Task")
        ordering = ('order',)

    @property
    def is_billable(self):
        return self.complete > 0

    def estimate_total_modify(self, worker, action, rate):
        for instance in self.taskinstances.all():
            instance.estimate_total_modify(worker, action, rate)

    @cached_property
    def instance(self):
        for instance in self.taskinstances.all():
            if instance.selected:
                return instance
        raise self.taskinstances.model.DoesNotExist

    @property
    def complete_percent(self):
        return round(self.complete / self.qty * 100) if self.qty else 0

    @property
    def unit_price(self):
        return self.instance.unit_price

    @property
    def fixed_price_estimate(self):
        return round(self.unit_price * self.qty, 2)

    @property
    def fixed_price_progress(self):
        return round(self.unit_price * self.complete, 2)

    @property
    def code(self):
        parent_code = self.taskgroup.code
        self_code = str(self.order + 1).zfill(self.taskgroup.job.project.task_zfill)
        return '{}.{}'.format(parent_code, self_code)

    def __str__(self):
        return '{} {}'.format(self.code, self.name)

    def clone_to(self, new_taskgroup, new_order):
        taskinstances = self.taskinstances.all()
        self.pk = None
        self.taskgroup = new_taskgroup
        self.order = new_order
        self.qty = 0.0
        self.complete = 0.0
        self.started_on = None
        self.completed_on = None
        self.status = ''
        self.save()
        for taskinstance in taskinstances:
            taskinstance.clone_to(self, taskinstance.order)


class TaskInstance(OrderedModel):
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
    unit_price = models.DecimalField(_("Price"), max_digits=14, decimal_places=4, default=0.0)

    # By default the first TaskInstance created for a task
    # will be the selected one.
    selected = models.BooleanField(default=False)

    task = models.ForeignKey(Task, related_name="taskinstances")
    order_with_respect_to = 'task'

    class Meta:
        verbose_name = _("Task Instance")
        verbose_name_plural = _("Task Instances")
        ordering = ['order']

    def estimate_total_modify(self, worker, action, rate):
        correction = self.lineitems.filter(is_correction=True).first()
        if action in ['increase', 'decrease']:
            correction = correction or LineItem(taskinstance=self, is_correction=True, price=0)
            correction.name = _("Price correction from %(worker)s on %(date)s") % \
                              {'worker': worker.get_full_name(), 'date': date_format(datetime.now())}
            correction.unit_qty = 1.0
            correction.unit = _("correction")
            direction = {'increase': 1, 'decrease': -1}[action]
            correction.price += self.unit_price * Decimal(rate) * direction
            correction.save()
        elif action == 'reset' and correction:
            correction.delete()

    @property
    def full_name(self):
        if not self.selected:
            return _("Alternative") + ": " + self.task.name + " " + self.name
        else:
            return self.task.name + " " + self.name

    @property
    def full_description(self):
        return self.task.description + " " + self.description

    @property
    def code(self):
        parent_code = self.task.code
        if self.task.taskinstances.count() > 1:
            return '{}{}'.format(parent_code, ascii_lowercase[self.order])
        else:
            return parent_code

    def __str__(self):
        return '{} {}'.format(self.code, self.name)

    def clone_to(self, new_task, new_order):
        lineitems = self.lineitems.exclude(is_correction=True).all()
        self.pk = None
        self.task = new_task
        self.order = new_order
        self.save()
        for lineitem in lineitems:
            lineitem.pk = None
            lineitem.is_flagged = False
            lineitem.taskinstance = self
            lineitem.save()


class LineItem(OrderedModel):

    name = models.CharField(_("Name"), max_length=512)

    # fixed billing, amount of hours or materials to complete just one unit of the task
    unit_qty = models.DecimalField(_("Quantity"), max_digits=14, decimal_places=4, default=0.0)

    # time and materials billing, amount of hours or materials to complete the entire task
    task_qty = models.DecimalField(_("Quantity"), max_digits=14, decimal_places=4, default=0.0)

    # time and materials billing, how many units of this have been delivered/expended and can thus be billed
    billable = models.DecimalField(_("Billable"), max_digits=14, decimal_places=4, default=0.0)

    # unit for the quantity
    unit = models.CharField(_("Unit"), max_length=64)

    # price per unit
    price = models.DecimalField(_("Price"), max_digits=14, decimal_places=4, default=0.0)

    # when labor is true, this will cause this line item to show up in time sheet and other
    # labor related parts of the system
    is_labor = models.BooleanField(default=False)

    # when material is true, this will cause this line item to show up in materials tracking
    # and other inventory parts of the system
    is_material = models.BooleanField(default=False)

    # flagged items will appear in the project dashboard as needing attention
    # could be set automatically by the system from temporal triggers (materials should have been delivered by now)
    # or it could be set manual by a user
    is_flagged = models.BooleanField(default=False)

    # this line item is a price correction
    is_correction = models.BooleanField(default=False)

    taskinstance = models.ForeignKey(TaskInstance, related_name="lineitems")
    order_with_respect_to = 'taskinstance'

    class Meta:
        verbose_name = _("Line Item")
        verbose_name_plural = _("Line Items")
        ordering = ('order',)

    @property
    def job(self):
        return self.taskinstance.task.job

    @property
    def project(self):
        return self.job.project


class ProgressReport(models.Model):
    # date and time when this progress report was filed
    timestamp = models.DateTimeField(auto_now_add=True)

    # description of what has been done
    comment = models.TextField()

    # how much of the project is complete in units of quantity
    # this gets copied into task.complete with the latest progress report value
    complete = models.DecimalField(_("Complete"), max_digits=14, decimal_places=4, default=0.0)

    task = models.ForeignKey(Task, related_name="progressreports")

    worker = models.ForeignKey('company.Worker', related_name="filedreports")

    @property
    def complete_percent(self):
        return round(self.complete / self.task.qty * 100) if self.task.qty else 0

    class Meta:
        verbose_name = _("Progress Report")
        verbose_name_plural = _("Progress Reports")
        ordering = ['-timestamp']


class ProgressAttachment(models.Model):
    report = models.ForeignKey(ProgressReport, related_name="attachments")
    attachment = models.FileField()

    class Meta:
        verbose_name = _("Attachment")
        verbose_name_plural = _("Attachments")
        ordering = ['id']
