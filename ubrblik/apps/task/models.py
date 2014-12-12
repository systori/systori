from django.db import models
from django.db.models import Sum, F
from django.utils.translation import ugettext_lazy as _


class TaskGroup(models.Model):
    name = models.CharField(_("Name"), max_length=128)
    project = models.ForeignKey("project.Project", related_name="taskgroups")
    class Meta:
        verbose_name = _("Task Group")
        verbose_name_plural = _("Task Groups")
        ordering = ['id']

    @property
    def total(self):
        # TODO: slow implementation, convert to aggregate
        t = 0
        for task in self.tasks.all():
            t += task.total
        return t

class Task(models.Model):
    name = models.CharField(_("Name"), max_length=128)
    taskgroup = models.ForeignKey("TaskGroup", related_name="tasks")
    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")
        ordering = ['id']

    @property
    def total(self):
        price = self.lineitems.aggregate(total=Sum('price', field='price*qty'))
        return price['total'] or 0


class LineItem(models.Model):

    HOUR = 'hour'
    DAY = 'day'
    WEEK = 'week'
    JOB = 'job'
    LABOR_UNIT = (
        (HOUR, _('Hour')),
        (DAY, _('Day')),
        (WEEK, _('Week')),
        (JOB, _('Job'))
    )

    M = 'm'
    M2 = 'm²'
    MATERIAL_UNIT = (
        (M, M),
        (M2, M2)
    )

    task = models.ForeignKey("Task", related_name="lineitems")
    unit = models.CharField(max_length=128, choices=LABOR_UNIT, default=JOB)
    name = models.CharField(_("Name"), max_length=128)
    qty = models.DecimalField(_("Quantity"), max_digits=12, decimal_places=2)
    price = models.DecimalField(_("Price"), max_digits=12, decimal_places=2)

    class Meta:
        ordering = ['id']

    @property
    def total(self):
        return self.price * self.qty
