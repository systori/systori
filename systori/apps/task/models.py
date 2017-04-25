import tsvector_field
from decimal import Decimal
from django.conf import settings
from django.contrib.postgres.search import SearchRank, SearchQuery
from django.db import models
from django.db.models.expressions import F, Q, RawSQL
from django.db.models.manager import BaseManager
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django_fsm import FSMField, transition
from django.utils.functional import cached_property
from systori.lib.utils import nice_percent

from systori.apps.company.models import LaborType
from systori.apps.inventory.models import MaterialType
from systori.apps.equipment.models import EquipmentType


class SearchableModelQuerySet(models.QuerySet):

    def search(self, terms, lang=settings.SEARCH_VECTOR_LANGUAGE):
        query = SearchQuery(terms, config=lang)
        field = self.model._meta.get_field('search')
        return (
            self.filter(search=query)
            .annotate(**{
                'match_'+column.name: tsvector_field.Headline(F(column.name), query, config=lang)
                for column in field.columns
            })
            .annotate(rank=SearchRank(F('search'), query))
            .order_by('-rank')
        )


class OrderedModel(models.Model):

    order = models.PositiveIntegerField(db_index=True)
    order_with_respect_to = None

    class Meta:
        abstract = True

    def get_ordering_queryset(self):
        assert self.order_with_respect_to is not None, "Subclasses of OrderbleModel must set order_with_respect_to."
        return self.__class__.objects.filter((self.order_with_respect_to, getattr(self, self.order_with_respect_to)))

    def save(self, *args, **kwargs):
        if self.order is None:
            c = self.get_ordering_queryset().aggregate(models.Max('order')).get('order__max')
            self.order = 1 if c is None else c + 1
        super().save(*args, **kwargs)


class GroupQuerySet(SearchableModelQuerySet):

    def groups_with_remaining_depth(self, remaining):
        """ Return all groups that have a specific depth to the right.
            When 'remaining' is,
                0: return all leaf groups
                1: there is exactly one other group between this one and the tasks
                ..
                3: maximum group depth for 'remaining'
        """
        assert 0 <= remaining <= 3
        q = Q()
        depth = remaining + 1
        while depth < 5:
            q |= Q(job__project__structure_depth=depth) & Q(depth=depth-remaining)
            depth += 1
        return self.filter(q)


class GroupManager(BaseManager.from_queryset(GroupQuerySet)):
    use_for_related_fields = True


class Group(OrderedModel):

    name = models.CharField(_("Name"), default="", blank=True, max_length=512)
    description = models.TextField(_("Description"), default="", blank=True)
    depth = models.PositiveIntegerField(editable=False, db_index=True)
    parent = models.ForeignKey('self', related_name='groups', null=True, on_delete=models.CASCADE)
    token = models.BigIntegerField('api token', null=True)
    job = models.ForeignKey('Job', null=True, related_name='all_groups', on_delete=models.CASCADE)
    search = tsvector_field.SearchVectorField([
        tsvector_field.WeightedColumn('name', 'A'),
        tsvector_field.WeightedColumn('description', 'D'),
    ], settings.SEARCH_VECTOR_LANGUAGE)
    order_with_respect_to = 'parent'

    objects = GroupManager()

    class Meta:
        verbose_name = _("Group")
        verbose_name_plural = _("Groups")
        ordering = ('order',)

    def __init__(self, *args, **kwargs):
        if 'parent' in kwargs:
            if 'job' not in kwargs:
                kwargs['job'] = kwargs['parent'].job
            if 'depth' not in kwargs:
                kwargs['depth'] = kwargs['parent'].depth+1
        super().__init__(*args, **kwargs)

    def refresh_pks(self):
        self.parent = self.parent
        self.job = self.job

    @property
    def is_root(self):
        return self.parent is None

    @property
    def _structure(self):
        return self.job.project.structure

    @cached_property
    def code(self):
        if self.name:
            code = self._structure.format_group(self.order, self.depth)
        else:
            code = '_'
        return code if self.is_root else "{}.{}".format(self.parent.code, code)

    def clone_to(self, new_parent, new_order):
        groups = self.groups.all()
        tasks = self.tasks.all()
        self.pk = None
        self.parent = new_parent
        self.job = new_parent.job
        self.order = new_order
        self.save()
        for group in groups:
            group.clone_to(self, group.order)
        for task in tasks:
            task.clone_to(self, task.order)

    def _calc(self, field):
        total = Decimal(0.0)
        for group in self.groups.all():
            total += getattr(group, field)
        for task in self.tasks.all():
            if field == 'estimate' and task.include_estimate:
                total += task.total
            elif field == 'progress':
                total += task.progress
        return total

    @property
    def estimate(self):
        if not hasattr(self, '_estimate'):
            self._estimate = self._calc('estimate')
        return self._estimate

    @estimate.setter
    def estimate(self, value):
        self._estimate = value

    @property
    def progress(self):
        if not hasattr(self, '_progress'):
            self._progress = self._calc('progress')
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value

    @cached_property
    def progress_percent(self):
        return nice_percent(self.progress, self.estimate)

    def __str__(self):
        return self.name


class JobQuerySet(models.QuerySet):

    IS_BILLABLE_SQL = """
        SELECT
            COUNT(task_task) > 0
        FROM
          task_task
        WHERE
          task_task.complete > 0 AND
          task_task.job_id = task_job.root_id
    """

    def with_is_billable(self):
        return self.annotate(is_billable=RawSQL(self.IS_BILLABLE_SQL, []))

    ESTIMATE_SQL = """
        SELECT
            COALESCE(SUM(task_task.total), 0)
        FROM
          task_task
        WHERE
          task_task.is_provisional = false AND
          task_task.variant_serial = 0 AND
          task_task.job_id = task_job.root_id
    """

    def with_estimate(self):
        return self.annotate(estimate=RawSQL(self.ESTIMATE_SQL, []))

    PROGRESS_SQL = """
        SELECT
            COALESCE(SUM(task_task.complete * task_task.price), 0)
        FROM
          task_task
        WHERE
          task_task.job_id = task_job.root_id
    """

    def with_progress(self):
        return self.annotate(progress=RawSQL(self.PROGRESS_SQL, []))

    def with_totals(self):
        return self.with_estimate().with_progress()

    def with_hierarchy(self, project):
        depth = project.structure.maximum_depth
        prefetch = []
        while depth > 0:
            prefetch.append('groups')
            depth -= 1
        prefetch += ['tasks', 'lineitems']
        return self.prefetch_related('__'.join(prefetch))


class JobManager(BaseManager.from_queryset(JobQuerySet)):
    use_for_related_fields = True


class Job(Group):
    account = models.OneToOneField('accounting.Account', related_name="job", null=True, on_delete=models.SET_NULL)
    root = models.OneToOneField('task.Group', parent_link=True, primary_key=True, related_name='+', on_delete=models.CASCADE)
    project = models.ForeignKey('project.Project', related_name="jobs", on_delete=models.CASCADE)
    order_with_respect_to = 'project'
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

    def __init__(self, *args, **kwargs):
        kwargs['depth'] = 0
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.name

    def refresh_pks(self):
        super().refresh_pks()
        self.project = self.project

    def save(self, *args, **kwargs):
        if self.job is not None and self.job_id is None:
            self.job = None
        super().save(*args, **kwargs)
        if self.job_id is None:
            self.job = self
            self.save()

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

    @transition(field=status, source="*", target=COMPLETED, custom={'label': _("Complete")})
    def complete(self):
        pass

    @property
    def can_propose(self):
        return self.status in Job.STATUS_FOR_PROPOSAL

    @property
    def can_complete(self):
        return self.status != Job.COMPLETED

    @property
    def can_delete(self):
        return self.status == Job.DRAFT

    @property
    def is_started(self):
        return self.status == Job.STARTED

    @property
    def is_billable(self):
        if not hasattr(self, '_is_billable'):
            self._is_billable = self.all_tasks.billable().exists()
        return self._is_billable

    @is_billable.setter
    def is_billable(self, value):
        self._is_billable = value

    def get_absolute_url(self):
        if self.project.is_template:
            return reverse('job.editor', args=[self.pk])
        else:
            return reverse('job.editor', args=[self.project.id, self.pk])

    def clone_to(self, new_job, *args):
        for group in self.groups.all():
            group.clone_to(new_job.root, None)


class TaskQuerySet(SearchableModelQuerySet):

    def billable(self):
        return self.filter(complete__gt=0)


class TaskManager(BaseManager.from_queryset(TaskQuerySet)):
    use_for_related_fields = True


class Task(OrderedModel):
    name = models.CharField(_("Name"), max_length=512)
    description = models.TextField(blank=True)
    search = tsvector_field.SearchVectorField([
        tsvector_field.WeightedColumn('name', 'A'),
        tsvector_field.WeightedColumn('description', 'D'),
    ], settings.SEARCH_VECTOR_LANGUAGE)

    qty = models.DecimalField(_("Quantity"), blank=True, null=True, max_digits=12, decimal_places=2, default=Decimal('0.00'))
    qty_equation = models.CharField(max_length=512, blank=True)
    complete = models.DecimalField(_("Completed"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    unit = models.CharField(_("Unit"), max_length=512, blank=True)
    price = models.DecimalField(_("Price"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    price_equation = models.CharField(max_length=512, blank=True)
    total = models.DecimalField(_("Total"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_equation = models.CharField(max_length=512, blank=True)

    started_on = models.DateField(blank=True, null=True)
    completed_on = models.DateField(blank=True, null=True)

    job = models.ForeignKey(Job, related_name="all_tasks", on_delete=models.CASCADE)
    group = models.ForeignKey(Group, related_name="tasks", on_delete=models.CASCADE)
    order_with_respect_to = 'group'

    # GAEB Spec 2.7.5.2
    variant_group = models.PositiveIntegerField(default=0)
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

    token = models.BigIntegerField('api token', null=True)

    objects = TaskManager()

    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Task")
        ordering = ('order',)

    def __init__(self, *args, **kwargs):
        if 'group' in kwargs and 'job' not in kwargs:
            kwargs['job'] = kwargs['group'].job
        super().__init__(*args, **kwargs)

    def refresh_pks(self):
        self.group = self.group
        self.job = self.job

    @property
    def is_billable(self):
        return self.complete > 0

    @property
    def is_variant(self):
        return self.variant_group > 0

    @property
    def is_time_and_materials(self):
        return self.qty is None

    @property
    def include_estimate(self):
        return not self.is_provisional and\
               self.variant_serial == 0

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
        if self.is_time_and_materials:
            progress = Decimal('0.00')
            for li in self.lineitems.all():
                progress += li.progress
            return progress
        else:
            return round(self.price * self.complete, 2)

    @property
    def complete_percent(self):
        if self.is_time_and_materials:
            expended = Decimal('0.00')
            qty = Decimal('0.00')
            for li in self.lineitems.all():
                if li.qty is not None:
                    qty += li.qty
                    expended += li.expended
            return nice_percent(expended, qty)
        else:
            return nice_percent(self.complete, self.qty)

    @property
    def code(self):
        code = self.group._structure.format_task(self.order)
        return '{}.{}'.format(self.group.code, code)

    @property
    def variant_allocation(self):
        return '{}.{}'.format(self.variant_group, self.variant_serial) \
                if self.is_variant else ''

    def __str__(self):
        return self.name

    def clone_to(self, new_group, new_order):
        lineitems = self.lineitems.all()
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
            lineitem.clone_to(self)


class ProgressReport(models.Model):
    # date and time when this progress report was filed
    timestamp = models.DateTimeField(auto_now_add=True)

    # description of what has been done
    comment = models.TextField()

    # how much of the project is complete in units of quantity
    # this gets copied into task.complete with the latest progress report value
    complete = models.DecimalField(_("Complete"), max_digits=12, decimal_places=2, default=Decimal('0.00'))

    task = models.ForeignKey(Task, related_name="progressreports", on_delete=models.CASCADE)
    worker = models.ForeignKey('company.Worker', related_name="progressreports", on_delete=models.CASCADE)

    @property
    def complete_percent(self):
        return round(self.complete / self.task.qty * 100) if self.task.qty else 0

    class Meta:
        verbose_name = _("Progress Report")
        verbose_name_plural = _("Progress Reports")
        ordering = ('-timestamp',)


class LineItem(OrderedModel):

    name = models.CharField(_("Name"), max_length=512, blank=True)

    qty = models.DecimalField(_("Quantity"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    qty_equation = models.CharField(max_length=512, blank=True)
    expended = models.DecimalField(_("Expended"), max_digits=12, decimal_places=2, default=Decimal('0.00'))

    unit = models.CharField(_("Unit"), max_length=512, blank=True)

    price = models.DecimalField(_("Price"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    price_equation = models.CharField(max_length=512, blank=True)

    total = models.DecimalField(_("Total"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_equation = models.CharField(max_length=512, blank=True)

    MATERIAL = "material"
    LABOR = "labor"
    EQUIPMENT = "equipment"
    OTHER = "other"
    LINEITEM_TYPES = (
        (MATERIAL, _("Material")),
        (LABOR, _("Labor")),
        (EQUIPMENT, _("Equipment")),
        (OTHER, _("Other")),
    )
    ICONS = {  # glyphicons
        MATERIAL: 'equalizer',
        LABOR: 'user',
        EQUIPMENT: 'wrench',
        OTHER: 'tasks',
    }
    lineitem_type = models.CharField(_('Line Item Type'), max_length=128, choices=LINEITEM_TYPES, default=OTHER)

    labor = models.ForeignKey(LaborType, null=True, related_name="lineitems", on_delete=models.SET_NULL)
    material = models.ForeignKey(MaterialType, null=True, related_name="lineitems", on_delete=models.SET_NULL)
    equipment = models.ForeignKey(EquipmentType, null=True, related_name="lineitems", on_delete=models.SET_NULL)

    task = models.ForeignKey(Task, related_name="lineitems", on_delete=models.CASCADE)
    order_with_respect_to = 'task'

    job = models.ForeignKey(Job, related_name="all_lineitems", on_delete=models.CASCADE)
    token = models.BigIntegerField('api token', null=True)

    # hidden lineitems are not included in the total
    is_hidden = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Line Item")
        verbose_name_plural = _("Line Items")
        ordering = ('order',)

    def __init__(self, *args, **kwargs):
        if 'task' in kwargs and 'job' not in kwargs:
            kwargs['job'] = kwargs['task'].job
        super().__init__(*args, **kwargs)

    @property
    def progress(self):
        return round(self.price * self.expended, 2)

    @property
    def is_material(self):
        return self.lineitem_type == self.MATERIAL

    @property
    def is_labor(self):
        return self.lineitem_type == self.LABOR

    @property
    def is_equipment(self):
        return self.lineitem_type == self.EQUIPMENT

    @property
    def is_other(self):
        return self.lineitem_type == self.OTHER

    @property
    def icon(self):
        return self.ICONS[self.lineitem_type]

    def refresh_pks(self):
        self.task = self.task
        self.job = self.job

    def clone_to(self, new_task):
        self.pk = None
        self.expended = 0.0
        self.task = new_task
        self.job = new_task.job
        self.save()


class ExpendReport(models.Model):
    # date and time when this progress report was filed
    timestamp = models.DateTimeField(auto_now_add=True)

    comment = models.TextField()

    # how much of the lineitem has been expended
    # this gets copied into lineitem.expended with the value from latest report
    expended = models.DecimalField(_("Expended"), max_digits=12, decimal_places=2, default=Decimal('0.00'))

    lineitem = models.ForeignKey(LineItem, related_name="expendreports", on_delete=models.CASCADE)
    worker = models.ForeignKey('company.Worker', related_name="expendreports", on_delete=models.CASCADE)

    @property
    def expended_percent(self):
        return round(self.expended / self.lineitem.qty * 100) if self.lineitem.qty else 0

    class Meta:
        verbose_name = _("Expend Report")
        verbose_name_plural = _("Expend Reports")
        ordering = ('-timestamp',)
