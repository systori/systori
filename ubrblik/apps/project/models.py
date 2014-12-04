from django.db import models
from django.utils.translation import ugettext_lazy as _

class Project(models.Model):
    name = models.CharField(_('Project Name'), max_length=128)
    description = models.TextField(_('Project Description'), blank=True, null=True)
    class Meta:
        ordering = ['name']
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")