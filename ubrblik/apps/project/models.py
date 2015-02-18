from decimal import Decimal
from django.db import models
from django.conf import settings
from ordered_model.models import OrderedModel
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_str
from django.core.urlresolvers import reverse
from ..task.models import Job
from geopy import geocoders

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
    
    job_offset = models.PositiveSmallIntegerField(_("Job Offset"), default=0)

    address = models.CharField(_("Address"), max_length=512)
    city = models.CharField(_("City"), max_length=512)
    postal_code = models.CharField(_("Postal Code"), max_length=512)
    country = models.CharField(_("Country"), max_length=512, default=settings.DEFAULT_COUNTRY)

    latitude = models.FloatField(_('Latitude'), null=True, blank=True)
    longitude = models.FloatField(_('Longitude'), null=True, blank=True)

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

    def save(self, *args, **kwargs):
        g = geocoders.GoogleV3()
        address = smart_str("{}, {}, {}, {}".format(self.address, self.city, self.postal_code, self.country))
        try:
            location = g.geocode(address)
            self.latitude = location.latitude
            self.longitude = location.longitude
        except:
            self.latitude = None
            self.longitude = None
        finally:
            super(Project, self).save(*args, **kwargs)

    @property
    def estimate_total(self):
        return self.jobs.estimate_total()

    @property
    def billable_total(self):
        return self.jobs.billable_total()

    @property
    def jobs_for_proposal(self):
        return self.jobs.filter(status=Job.DRAFT)

    @property
    def has_jobs_for_proposal(self):
        return self.jobs_for_proposal.exists() and self.has_billable_contact

    @property
    def jobs_for_invoice(self):
        return self.jobs.filter(status=Job.STARTED)

    @property
    def has_jobs_for_invoice(self):
        return self.jobs_for_invoice.exists() and self.has_billable_contact
    
    @property
    def billable_contact(self):
        try:
            return self.project_contacts.filter(is_billable=True).get()
        except self.project_contacts.model.DoesNotExist:
            return None

    @property
    def has_billable_contact(self):
        return self.billable_contact != None