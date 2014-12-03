from django.db import models
from django.db.models import Sum, F
from django.utils.translation import ugettext_lazy as _


class TaskGroup(models.Model):
    name = models.CharField(_("Name"), max_length=128)
    project = models.ForeignKey("project.Project", related_name="task_groups")


class Task(models.Model):
    name = models.CharField(_("Name"), max_length=128)
    group = models.ForeignKey("TaskGroup", related_name="tasks")
    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")
    
    @property
    def total(self):
        total = 0

        labor_cost = self.labor.aggregate(total=Sum('cost', field='cost*qty'))
        total += labor_cost['total'] if labor_cost['total']!=None else 0

        material_cost = self.materials.aggregate(total=Sum('cost', field='cost*qty'))
        total += material_cost['total'] if material_cost['total']!=None else 0

        return total


class LineItem(models.Model):
    name = models.CharField(_("Name"), max_length=128)
    cost = models.DecimalField(_("Cost"), max_digits=10, decimal_places=2)
    qty = models.IntegerField(_("Quantity"))
    class Meta:
        abstract = True

    @property
    def total(self):
        return self.cost * self.qty


class Labor(LineItem):
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
    task = models.ForeignKey("Task", related_name="labor")
    unit = models.CharField(max_length=128, choices=LABOR_UNIT, default=JOB)


class Material(LineItem):
    M = 'm'
    M2 = 'm²'
    MATERIAL_UNIT = (
        (M, M),
        (M2, M2)
    )
    task = models.ForeignKey("Task", related_name="materials")
    unit = models.CharField(max_length=128, choices=MATERIAL_UNIT)
