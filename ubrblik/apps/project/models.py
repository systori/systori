from decimal import Decimal
from django.db import models
from ordered_model.models import OrderedModel
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from ..task.models import Job

class ProjectQuerySet(models.QuerySet):

    def template(self):
        return self.filter(is_template=True)

    def without_template(self):
        return self.exclude(is_template=True)

class Project(models.Model):

    name = models.CharField(_('Project Name'), max_length=512)
    description = models.TextField(_('Project Description'), blank=True, null=True)
    is_template = models.BooleanField(default=False)

    job_zfill = models.PositiveSmallIntegerField(_("Job Code Zero Fill"), default=1)
    taskgroup_zfill = models.PositiveSmallIntegerField(_("Task Group Code Zero Fill"), default=1)
    task_zfill = models.PositiveSmallIntegerField(_("Task Code Zero Fill"), default=1)

    objects = ProjectQuerySet.as_manager()

    def get_absolute_url(self):
        if self.is_template:
            return reverse('templates')
        else:
            return reverse('project.view', args=[self.id])

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ['name']

    def _calc_total(self, calc_type):
        field = '{}_total'.format(calc_type)
        t = 0
        for job in self.jobs.all():
            t += getattr(job, field)
        return t

    @property
    def estimate_total(self):
        return sum([job.estimate_total for job in self.jobs.all()])

    @property
    def billable_total(self):
        return sum([job.billable_total for job in self.jobs.all()])
    
    @property
    def jobs_for_proposal(self):
        return self.jobs.filter(status=Job.DRAFT)

    @property
    def has_jobs_for_proposal(self):
        return self.jobs_for_proposal.exists()

    @property
    def jobs_for_invoice(self):
        return self.jobs.filter(status=Job.STARTED)

    @property
    def has_jobs_for_invoice(self):
        return self.jobs_for_invoice.exists()