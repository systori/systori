from math import floor, ceil
from datetime import date
from django.db import models
from django.conf import settings
from django.utils.translation import pgettext_lazy, ugettext_lazy as _
from django.utils.encoding import smart_str
from django.core.urlresolvers import reverse
from django_fsm import FSMField, transition
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

    # level 1 is Job/Lot which is not optional and cannot be named something other than "Lot" (per GAEB spec)
    level_1_zfill = models.PositiveSmallIntegerField(_("Level %(num)s Zero Fill") % {'num': 1}, default=1)

    # eg. Main Section
    has_level_2 = models.BooleanField(default=True)
    level_2_zfill = models.PositiveSmallIntegerField(_("Level %(num)s Zero Fill") % {'num': 2}, default=1)
    level_2_name = models.CharField(_('Level %(num)s Name') % {'num': 2}, max_length=512,
                                    default=pgettext_lazy('level', "Main Section"))

    # eg. Section
    has_level_3 = models.BooleanField(default=False)
    level_3_zfill = models.PositiveSmallIntegerField(_("Level %(num)s Zero Fill") % {'num': 3}, default=1)
    level_3_name = models.CharField(_('Level %(num)s Name') % {'num': 3}, max_length=512,
                                    default=pgettext_lazy('level', "Section"))

    # eg. Sub Section
    has_level_4 = models.BooleanField(default=False)
    level_4_zfill = models.PositiveSmallIntegerField(_("Level %(num)s Zero Fill") % {'num': 4}, default=1)
    level_4_name = models.CharField(_('Level %(num)s Name') % {'num': 4}, max_length=512,
                                    default=pgettext_lazy('level', "Sub-Section"))

    # eg. Title
    has_level_5 = models.BooleanField(default=False)
    level_5_zfill = models.PositiveSmallIntegerField(_("Level %(num)s Zero Fill") % {'num': 5}, default=1)
    level_5_name = models.CharField(_('Level %(num)s Name') % {'num': 5}, max_length=512,
                                    default=pgettext_lazy('level', "Title"))

    # Work Item
    task_zfill = models.PositiveSmallIntegerField(_("Task Code Zero Fill"), default=1)

    account = models.OneToOneField('accounting.Account', related_name="project", null=True)

    objects = ProjectQuerySet.as_manager()

    PROSPECTIVE = "prospective"
    TENDERING = "tendering"
    PLANNING = "planning"
    EXECUTING = "executing"
    SETTLEMENT = "settlement"
    WARRANTY = "warranty"
    FINISHED = "finished"

    PHASE_CHOICES = (
        (PROSPECTIVE, pgettext_lazy('phase', "Prospective")),
        (TENDERING, pgettext_lazy('phase', "Tendering")),
        (PLANNING, pgettext_lazy('phase', "Planning")),
        (EXECUTING, pgettext_lazy('phase', "Executing")),
        (SETTLEMENT, pgettext_lazy('phase', "Settlement")),
        (WARRANTY, pgettext_lazy('phase', "Warranty")),
        (FINISHED, pgettext_lazy('phase', "Finished"))
    )

    # Floating phases support moving between each other relatively
    # freely and consequence free. Once you get to SETTLEMENT phase
    # then legal/accounting stuff kick in and it's not a good idea
    # to move back to the floating phases.
    FLOATING_PHASES = [PROSPECTIVE, TENDERING, PLANNING, EXECUTING]

    phase = FSMField(default=PROSPECTIVE, choices=PHASE_CHOICES)

    @transition(field=phase, source=FLOATING_PHASES, target=PROSPECTIVE)
    def begin_prospecting(self):
        pass

    @property
    def is_prospective(self):
        return self.phase == Project.PROSPECTIVE

    @transition(field=phase, source=FLOATING_PHASES, target=TENDERING)
    def begin_tendering(self):
        pass

    @property
    def is_tendering(self):
        return self.phase == Project.TENDERING

    @transition(field=phase, source=FLOATING_PHASES, target=PLANNING)
    def begin_planning(self):
        pass

    @property
    def is_planning(self):
        return self.phase == Project.PLANNING

    @transition(field=phase, source=FLOATING_PHASES, target=EXECUTING)
    def begin_executing(self):
        pass

    @property
    def is_executing(self):
        return self.phase == Project.EXECUTING

    @transition(field=phase, source=FLOATING_PHASES, target=SETTLEMENT)
    def begin_settlement(self):
        pass

    @property
    def is_settlement(self):
        return self.phase == Project.SETTLEMENT

    @transition(field=phase, source=FLOATING_PHASES+[SETTLEMENT], target=WARRANTY)
    def begin_warranty(self):
        pass

    @property
    def is_warranty(self):
        return self.phase == Project.WARRANTY

    @transition(field=phase, source="*", target=FINISHED)
    def finish(self):
        pass

    @property
    def is_finished(self):
        return self.phase == Project.FINISHED

    def phases(self, worker):
        phases = []
        available = list(self.get_available_user_phase_transitions(worker.user))
        is_past = True
        for name, label in self.PHASE_CHOICES:

            if self.phase == name:
                is_past = False

            transition_name = None
            for transition in available:
                if transition.target == name:
                    transition_name = transition.name
                    break

            phases.append((name, label, self.phase == name, is_past, transition_name))

        return phases

    ACTIVE = "active"
    PAUSED = "paused"
    DISPUTED = "disputed"
    STOPPED = "stopped"

    STATE_CHOICES = (
        (ACTIVE, _("Active")),
        (PAUSED, _("Paused")),
        (DISPUTED, _("Disputed")),
        (STOPPED, _("Stopped"))
    )

    state = FSMField(default=ACTIVE, choices=STATE_CHOICES)

    @transition(field=state, source="*", target=ACTIVE)
    def activate(self):
        pass

    @transition(field=state, source="*", target=PAUSED)
    def pause(self):
        pass

    @transition(field=state, source="*", target=DISPUTED)
    def dispute(self):
        pass

    @transition(field=state, source="*", target=STOPPED)
    def stop(self):
        pass

    def states(self, worker):
        states = []
        available = list(self.get_available_user_state_transitions(worker.user))
        for name, label in self.STATE_CHOICES:

            transition_name = None
            for transition in available:
                if transition.target == name:
                    transition_name = transition.name
                    break

            states.append((name, label, self.state == name, transition_name))

        return states

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

    @staticmethod
    def prefetch(project_id):
        return \
            Project.objects.filter(id=project_id) \
                .prefetch_related('jobs__taskgroups__tasks__taskinstances__lineitems') \
                .get()

    @property
    def estimate_total(self):
        return self.jobs.estimate_total()

    @property
    def progress_total(self):
        return self.jobs.progress_total()

    @property
    def progress_percent(self):
        percent = self.progress_total / self.estimate_total * 100 if self.estimate_total else 0
        if percent < 100:
            return floor(percent)
        elif percent > 100:
            return ceil(percent)
        else:
            return 100

    @property
    def jobs_for_proposal(self):
        return self.jobs.filter(status__in=Job.STATUS_FOR_PROPOSAL)

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
        return self.billable_contact is not None


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
    travel_time = models.PositiveIntegerField(
        _("Travel time"), null=True, blank=True, help_text=_("in minutes"))

    def __str__(self):
        return self.name

    def save(self, *args, skip_geocoding=False, **kwargs):
        try:
            if not skip_geocoding:
                g = geocoders.GoogleV3()
                address = smart_str("{}, {}, {}, {}".format(self.address, self.city, self.postal_code, self.country))
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
    workers = models.ManyToManyField('company.Worker', through='TeamMember', related_name="dailyplans")
    tasks = models.ManyToManyField('task.Task', related_name="dailyplans")
    equipment = models.ManyToManyField('equipment.Equipment', through='EquipmentAssignment', related_name="dailyplans")

    notes = models.TextField(blank=True)

    objects = DailyPlanQuerySet.as_manager()

    @property
    def is_today(self):
        return self.day == date.today()

    @property
    def url_id(self):
        return '{}-{}'.format(self.day.isoformat(), self.id or 0)

    def is_worker_assigned(self, worker):
        return self.members.filter(worker=worker).exists()

    class Meta:
        ordering = ['-day']


class TeamMember(models.Model):
    """ When a worker is assigned to a DailyPlan we need to record
        if they are a foreman or a regular worker.
    """
    dailyplan = models.ForeignKey(DailyPlan, related_name="members")
    worker = models.ForeignKey('company.Worker', related_name="assignments")
    is_foreman = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_foreman', 'worker__user__first_name']


class EquipmentAssignment(models.Model):
    dailyplan = models.ForeignKey(DailyPlan, related_name="assigned_equipment")
    equipment = models.ForeignKey('equipment.Equipment', related_name="assignments")
