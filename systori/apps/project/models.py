from decimal import Decimal
from datetime import date
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

    account = models.OneToOneField('accounting.Account', related_name="project", null=True)

    objects = ProjectQuerySet.as_manager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        if self.is_template:
            return reverse('templates')
        else:
            return reverse('project.view', args=[self.id])

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ['name']

    @property
    def billable_jobs(self):
        for job in self.jobs.all():
            if job.is_billable:
                yield job

    @property
    def is_billable(self):
        for job in self.billable_jobs:
            return True
        return False

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
    def billable_contact(self):
        try:
            return self.project_contacts.filter(is_billable=True).get()
        except self.project_contacts.model.DoesNotExist:
            return None

    @property
    def has_billable_contact(self):
        return self.billable_contact != None


class JobSite(models.Model):
    """ A project can have one or more job sites. """

    project = models.ForeignKey(Project, related_name="jobsites")
    name = models.CharField(_('Site Name'), max_length=512)

    address = models.CharField(_("Address"), max_length=512)
    city = models.CharField(_("City"), max_length=512)
    postal_code = models.CharField(_("Postal Code"), max_length=512)
    country = models.CharField(_("Country"), max_length=512, default=settings.DEFAULT_COUNTRY)

    latitude = models.FloatField(_("Latitude"), null=True, blank=True)
    longitude = models.FloatField(_("Longitude"), null=True, blank=True)

    def __str__(self):
        return self.name

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
            super(JobSite, self).save(*args, **kwargs)


class DailyPlanQuerySet(models.QuerySet):

    def today(self):
        return self.filter(day=date.today())


class DailyPlan(models.Model):
    """ Daily Plan contains a list of tasks that are planned for the day,
        a list of workers performing the tasks and a job site at which they
        will perform the tasks. All on a particular day.
    """
    jobsite = models.ForeignKey(JobSite, related_name="dailyplans")
    day = models.DateField(_("Day"), default=date.today)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='TeamMember', related_name="dailyplans")
    tasks = models.ManyToManyField('task.Task', related_name="dailyplans")
    equipment = models.ManyToManyField('equipment.Equipment', related_name="dailyplans")

    notes = models.TextField(blank=True)

    objects = DailyPlanQuerySet.as_manager()

    @property
    def is_today(self):
        return self.day == date.today()

    @property
    def url_id(self):
        return '{}-{}'.format(self.day.isoformat(), self.id or 0)

    class Meta:
        ordering = ['-day']


class TeamMember(models.Model):
    """ When a worker is assigned to a DailyPlan we need to record
        if they are a foreman or a regular worker.
    """
    dailyplan = models.ForeignKey(DailyPlan, related_name="workers")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="assignments")
    is_foreman = models.BooleanField(default=False)
    class Meta:
        ordering = ['-is_foreman', 'user__first_name']