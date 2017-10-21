from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models.expressions import RawSQL
from django.urls import reverse
from django.utils.encoding import smart_str
from django.utils.functional import cached_property
from django.utils.timezone import localdate
from django.utils.translation import pgettext_lazy, ugettext_lazy as _
from django_fsm import FSMField, transition
from geopy import geocoders

from systori.apps.task.gaeb.structure import GAEBStructureField
from systori.lib.utils import nice_percent
from ..task.models import Job, JobQuerySet


def _job_annotation(type, inner):
    return "SELECT {} FROM task_job WHERE task_job.project_id=project_project.id".format({
        'bool': "COALESCE(BOOL_OR(({})), false)".format(inner),
        'sum': "COALESCE(SUM(({})), 0)".format(inner),
    }[type])


class ProjectQuerySet(models.QuerySet):

    IS_BILLABLE_SQL = _job_annotation('bool', JobQuerySet.IS_BILLABLE_SQL)
    ESTIMATE_SQL = _job_annotation('sum', JobQuerySet.ESTIMATE_SQL)
    PROGRESS_SQL = _job_annotation('sum', JobQuerySet.PROGRESS_SQL)

    def with_is_billable(self):
        return self.annotate(is_billable=RawSQL(self.IS_BILLABLE_SQL, []))

    def with_estimate(self):
        return self.annotate(estimate=RawSQL(self.ESTIMATE_SQL, []))

    def with_progress(self):
        return self.annotate(progress=RawSQL(self.PROGRESS_SQL, []))

    def with_totals(self):
        return self.with_estimate().with_progress()

    def template(self):
        return self.filter(is_template=True)

    def without_template(self):
        return self.exclude(is_template=True)


class Project(models.Model):
    name = models.CharField(_('Project Name'), max_length=512)
    description = models.TextField(_('Project Description'), blank=True, null=True)
    is_template = models.BooleanField(default=False)
    structure = GAEBStructureField(_('Numbering Structure'), default="01.01.001")

    notes = GenericRelation('main.Note')

    objects = ProjectQuerySet.as_manager()

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ['name']

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

    @transition(field=phase, source="*", target=PROSPECTIVE)
    def begin_prospecting(self):
        pass

    @property
    def is_prospective(self):
        return self.phase == Project.PROSPECTIVE

    @transition(field=phase, source="*", target=TENDERING)
    def begin_tendering(self):
        pass

    @property
    def is_tendering(self):
        return self.phase == Project.TENDERING

    @transition(field=phase, source="*", target=PLANNING)
    def begin_planning(self):
        pass

    @property
    def is_planning(self):
        return self.phase == Project.PLANNING

    @transition(field=phase, source="*", target=EXECUTING)
    def begin_executing(self):
        pass

    @property
    def is_executing(self):
        return self.phase == Project.EXECUTING

    @transition(field=phase, source="*", target=SETTLEMENT)
    def begin_settlement(self):
        pass

    @property
    def is_settlement(self):
        return self.phase == Project.SETTLEMENT

    @transition(field=phase, source="*", target=WARRANTY)
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

    @property
    def is_billable(self):
        if not hasattr(self, '_is_billable'):
            raise ValueError(
                'Project instance created without using with_is_billable() annotation.'
                'Hint: Project.objects.with_is_billable()'
            )
        return self._is_billable

    @is_billable.setter
    def is_billable(self, value):
        self._is_billable = value

    @property
    def estimate(self):
        if not hasattr(self, '_estimate'):
            raise ValueError(
                'Project instance created without using with_estimate() annotation.'
                'Hint: Project.objects.with_estimate() or Project.objects.with_totals()'
            )
        return self._estimate

    @estimate.setter
    def estimate(self, value):
        self._estimate = value

    @property
    def progress(self):
        if not hasattr(self, '_progress'):
            raise ValueError(
                'Project instance created without using with_progress() annotation.'
                'Hint: Project.objects.with_progress() or Project.objects.with_totals()'
            )
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value

    @cached_property
    def progress_percent(self):
        return nice_percent(self.progress, self.estimate)

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

    def can_receive_job(self, source_job):
        return self.structure_depth == source_job.project.structure_depth

    def receive_job(self, source_job):
        if self.can_receive_job(source_job):
            new_job = Job.objects.create(project=self, name=source_job.name, order=None)
            source_job.clone_to(new_job)
            return True
        return False


class JobSite(models.Model):
    """ A project can have one or more job sites. """

    project = models.ForeignKey(Project, related_name="jobsites", on_delete=models.CASCADE)
    name = models.CharField(_('Site Name'), max_length=512)

    address = models.CharField(_("Address"), max_length=512)
    city = models.CharField(_("City"), max_length=512)
    postal_code = models.CharField(_("Postal Code"), max_length=512)
    country = models.CharField(_("Country"), max_length=512, default=settings.DEFAULT_COUNTRY)

    latitude = models.FloatField(_("Latitude"), null=True, blank=True)
    longitude = models.FloatField(_("Longitude"), null=True, blank=True)
    travel_time = models.PositiveIntegerField(
        _("Travel time"), null=True, blank=True, help_text=_("in minutes"))

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.name

    def geocode_address(self):
        if settings.GEOCODE_ADDRESSES:
            try:
                g = geocoders.GoogleV3()
                address = smart_str("{}, {}, {}, {}".format(
                    self.address,
                    self.city, self.postal_code,
                    self.country
                ))
                location = g.geocode(address)
                self.latitude = location.latitude
                self.longitude = location.longitude
            except:
                self.latitude = None
                self.longitude = None


class DailyPlanQuerySet(models.QuerySet):
    def today(self):
        return self.filter(day=localdate())


class DailyPlan(models.Model):
    """ Daily Plan contains a list of tasks that are planned for the day,
        a list of workers performing the tasks and a job site at which they
        will perform the tasks. All on a particular day.
    """
    jobsite = models.ForeignKey(JobSite, related_name="dailyplans", on_delete=models.CASCADE)
    day = models.DateField(_("Day"), default=localdate)
    workers = models.ManyToManyField('company.Worker', through='TeamMember', related_name="dailyplans")
    tasks = models.ManyToManyField('task.Task', related_name="dailyplans")
    equipment = models.ManyToManyField('equipment.Equipment', through='EquipmentAssignment', related_name="dailyplans")

    notes = models.TextField(blank=True)

    objects = DailyPlanQuerySet.as_manager()

    @property
    def is_today(self):
        return self.day == localdate()

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
    dailyplan = models.ForeignKey(DailyPlan, related_name="members", on_delete=models.CASCADE)
    worker = models.ForeignKey('company.Worker', related_name="assignments", on_delete=models.CASCADE)
    is_foreman = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_foreman', 'worker__user__first_name']


class EquipmentAssignment(models.Model):
    dailyplan = models.ForeignKey(DailyPlan, related_name="assigned_equipment", on_delete=models.CASCADE)
    equipment = models.ForeignKey('equipment.Equipment', related_name="assignments", on_delete=models.CASCADE)
