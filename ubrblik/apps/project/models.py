from decimal import Decimal
from django.db import models
from ordered_model.models import OrderedModel
from django.utils.translation import ugettext_lazy as _


class Project(models.Model):

    name = models.CharField(_('Project Name'), max_length=128)
    description = models.TextField(_('Project Description'), blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")

    @property
    def total(self):
        t = 0
        for job in self.jobs.all():
            t += job.total
        return t

    @property
    def tax(self):
        return self.total * Decimal(.19)

    @property
    def total_gross(self):
        return self.total * Decimal(1.19)

