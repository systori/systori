import re
from decimal import Decimal
from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django_fsm import FSMField, transition
from django.utils.functional import cached_property
from systori.lib.utils import nice_percent


class OrderedModel(models.Model):

    order = models.PositiveIntegerField(editable=False, db_index=True)
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
            self.order = 1 if c is None else c + 1
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


class Group(OrderedModel):

    name = models.CharField(_("Name"), default="", blank=True, max_length=512)
    description = models.TextField(_("Description"), default="", blank=True)
    parent = models.ForeignKey('self', related_name='groups', null=True)
    token = models.IntegerField('api token', null=True)
    job = models.ForeignKey('Job', null=True, related_name='all_groups')
    order_with_respect_to = 'parent'

    class Meta:
        verbose_name = _("Group")
        verbose_name_plural = _("Groups")
        ordering = ('order',)

    @property
    def _structure(self):
        return self.job.project.structure

    @property
    def is_root(self):
        return self.parent is None

    @cached_property
    def level(self):
        return 0 if self.is_root else self.parent.level + 1

    @cached_property
    def code(self):
        if self.name:
            code = self._structure.format_group(self.order, self.level)
        else:
            code = '_'
        return code if self.is_root else "{}.{}".format(self.parent.code, code)

    def clone_to(self, new_group, new_order):
        groups = self.groups.all()
        tasks = self.tasks.all()
        self.pk = None
        self.parent = new_group
        self.job = new_group.job
        self.order = new_order
        self.save()
        for group in groups:
            group.clone_to(self, group.order)
        for task in tasks:
            task.clone_to(self, task.order)

    def generate_groups(self):
        if self._structure.has_level(self.level+1):
            Group.objects.create(parent=self, job=self.job).generate_groups()

    def _calc(self, field):
        total = Decimal(0.0)
        for group in self.groups.all():
            total += getattr(group, field)
        for task in self.tasks.all():
            if field != 'total' or task.include_estimate:
                total += getattr(task, field)
        return total

    @property
    def total(self):
        return self._calc('total')

    @property
    def progress(self):
        return self._calc('progress')

    @property
    def progress_percent(self):
        return nice_percent(self.progress, self.total)

    def __str__(self):
        return self.name


class JobQuerySet(models.QuerySet):

    def total(self):
        return sum([job.total for job in self])

    def progress(self):
        return sum([job.progress for job in self])

    def prefetch_groups(self, project):
        level = 3
        prefetch = []
        while self.has_level(level):
            prefetch.append('children')
            level += 1
        prefetch += ['tasks', 'lineitems']
        return list(
            self._taskgroups
                .filter(level=2)
                .prefetch_related('__'.join(prefetch))
                .all()
        )


class JobManager(BaseManager.from_queryset(JobQuerySet)):
    use_for_related_fields = True


class Job(Group):
    account = models.OneToOneField('accounting.Account', related_name="job", null=True, on_delete=models.SET_NULL)
    root = models.OneToOneField('task.Group', parent_link=True, primary_key=True, related_name='+')
    project = models.ForeignKey('project.Project', related_name="jobs")
    order_with_respect_to = 'project'

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

    @property
    def can_propose(self):
        return self.status in self.STATUS_FOR_PROPOSAL

    def clone_to(self, new_job, *args):
        for group in self.groups.all():
            group.clone_to(new_job.root, None)

    @property
    def is_billable(self):
        for task in self.all_tasks.all():
            if task.is_billable:
                return True
        return False

    def get_absolute_url(self):
        if self.project.is_template:
            return reverse('job.editor', args=[self.pk])
        else:
            return reverse('job.editor', args=[self.project.id, self.pk])

    def __str__(self):
        return self.name


class Task(OrderedModel):
    name = models.CharField(_("Name"), max_length=512)
    description = models.TextField(blank=True)

    qty = models.DecimalField(_("Quantity"), max_digits=14, decimal_places=4, default=0.0)
    qty_equation = models.CharField(max_length=512, blank=True)
    complete = models.DecimalField(_("Completed"), max_digits=14, decimal_places=4, default=0.0)
    unit = models.CharField(_("Unit"), max_length=512, blank=True)
    price = models.DecimalField(_("Price"), max_digits=14, decimal_places=4, default=0.0)
    price_equation = models.CharField(max_length=512, blank=True)
    total = models.DecimalField(_("Total"), max_digits=14, decimal_places=4, default=0.0)
    total_equation = models.CharField(max_length=512, blank=True)

    started_on = models.DateField(blank=True, null=True)
    completed_on = models.DateField(blank=True, null=True)

    job = models.ForeignKey(Job, related_name="all_tasks")
    group = models.ForeignKey(Group, related_name="tasks")
    order_with_respect_to = 'group'

    # GAEB Spec 2.7.5.2
    variant_group = models.PositiveIntegerField(null=True)
    variant_serial = models.PositiveIntegerField(default=0)

    # GAEB Spec 2.7.5.3
    is_provisional = models.BooleanField(default=False)

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

    token = models.IntegerField('api token', null=True)

    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Task")
        ordering = ('order',)

    def __init__(self, *args, **kwargs):
        if 'job' not in kwargs and 'group' in kwargs:
            kwargs['job'] = kwargs['group'].job
        super().__init__(*args, **kwargs)

    @property
    def is_billable(self):
        return self.complete > 0

    @property
    def is_variant(self):
        return self.variant_group is not None

    @property
    def include_estimate(self):
        if self.is_provisional:
            return False
        if self.is_variant and self.variant_serial != 0:
            return False
        return True

    @property
    def lineitem_price(self):
        """ The task price as defined by lineitems.
            For most cases, use the Task.price instead of this.
        """
        price = Decimal('0.00')
        for li in self.lineitems.all():
            price += li.total
        return price

    @property
    def price_difference(self):
        """ Normally the Task.price == lineitem_price and thus diff is 0.
            In cases where the user has defined the total manually and then the
            lineitem_price (sum of lineitem totals) != Task.price
            this will return the amount of the discrepancy.
        """
        return self.price - self.lineitem_price

    @property
    def progress(self):
        return round(self.price * self.complete, 2)

    @property
    def complete_percent(self):
        return nice_percent(self.complete, self.qty)

    @property
    def code(self):
        code = self.group._structure.format_task(self.order)
        return '{}.{}'.format(self.group.code, code)

    def __str__(self):
        return self.name

    def clone_to(self, new_group, new_order):
        lineitems = self.lineitems.exclude(is_correction=True).all()
        self.pk = None
        self.group = new_group
        self.job = new_group.job
        self.order = new_order
        self.complete = 0.0
        self.started_on = None
        self.completed_on = None
        self.status = ''
        self.save()
        for lineitem in lineitems:
            lineitem.pk = None
            lineitem.complete = 0.0
            lineitem.is_flagged = False
            lineitem.task = self
            lineitem.job = self.job
            lineitem.save()


class LineItem(OrderedModel):

    name = models.CharField(_("Name"), max_length=512, blank=True)

    qty = models.DecimalField(_("Quantity"), max_digits=14, decimal_places=4, default=0.0)
    qty_equation = models.CharField(max_length=512, blank=True)
    complete = models.DecimalField(_("Completed"), max_digits=14, decimal_places=4, default=0.0)

    unit = models.CharField(_("Unit"), max_length=512, blank=True)

    price = models.DecimalField(_("Price"), max_digits=14, decimal_places=4, default=0.0)
    price_equation = models.CharField(max_length=512, blank=True)

    total = models.DecimalField(_("Total"), max_digits=14, decimal_places=4, default=0.0)
    total_equation = models.CharField(max_length=512, blank=True)

    # flagged items will appear in the project dashboard as needing attention
    # could be set automatically by the system from temporal triggers (materials should have been delivered by now)
    # or it could be set manual by a user
    is_flagged = models.BooleanField(default=False)

    # hidden lineitems are not included in the total
    is_hidden = models.BooleanField(default=False)

    # this line item is a price correction
    is_correction = models.BooleanField(default=False)

    task = models.ForeignKey(Task, related_name="lineitems")
    order_with_respect_to = 'task'

    job = models.ForeignKey(Job, related_name="all_lineitems")
    token = models.IntegerField('api token', null=True)

    class Meta:
        verbose_name = _("Line Item")
        verbose_name_plural = _("Line Items")
        ordering = ('order',)

    def __init__(self, *args, **kwargs):
        if 'job' not in kwargs and 'task' in kwargs:
            kwargs['job'] = kwargs['task'].job
        super().__init__(*args, **kwargs)

    @property
    def project(self):
        return self.job.project

    # regex should math the one in dart app spreadsheet/cell.dart
    NUMBER = re.compile(r"^-?[0-9.,]+$")

    def _is_equation(self, column):
        val = getattr(self, column+'_equation')
        if not val:
            return False
        if self.NUMBER.search(val):
            return False
        return True
    is_qty_equation = property(lambda self: self._is_equation('qty'))
    is_price_equation = property(lambda self: self._is_equation('price'))
    is_total_equation = property(lambda self: self._is_equation('total'))


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
        ordering = ('-timestamp',)


class ProgressAttachment(models.Model):
    report = models.ForeignKey(ProgressReport, related_name="attachments")
    attachment = models.FileField()

    class Meta:
        verbose_name = _("Attachment")
        verbose_name_plural = _("Attachments")
        ordering = ('id',)
