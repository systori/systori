from datetime import date, time
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property

from postgres_schema.models import AbstractSchema
from timezone_field import TimeZoneField

from systori.lib.fields import RateType
from ..timetracking.utils import BreakSpan


class Company(AbstractSchema):
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Worker', blank=True, related_name='companies')
    timezone = TimeZoneField(default=settings.TIME_ZONE)
    is_jobsite_required = models.BooleanField(
        _('Jobsite Required'), default=True,
        help_text=_('Require that all projects have a jobsite.')
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    def url(self, request):
        port = ''
        if ':' in request.META['HTTP_HOST']:
            port = ':'+request.META['HTTP_HOST'].split(':')[1]
        return request.scheme+'://'+self.schema+'.'+settings.SERVER_NAME+port

    def active_workers(self, **params):
        return self.workers \
            .select_related('user', 'contract')\
            .filter(is_active=True, **params)\
            .order_by('user__last_name')

    def tracked_workers(self):
        return self.active_workers(contract__requires_time_tracking=True)

    def activate(self):
        super().activate()
        timezone.activate(self.timezone)

    def __str__(self):
        return _('Company') + ' {} ({}.systori.com)'.format(self.name, self.schema)


class Worker(models.Model):
    company = models.ForeignKey('Company', related_name="workers", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="access", on_delete=models.CASCADE)
    labor_types = models.ManyToManyField('LaborType', blank=True, related_name="workers")
    contract = models.ForeignKey('Contract', null=True, related_name="+", on_delete=models.SET_NULL)

    class Meta:
        unique_together = ("company", "user")

    is_owner = models.BooleanField(
        _('Owner'), default=False,
        help_text=_('Has full and unlimited access.')
    )

    is_staff = models.BooleanField(
        _('Staff'), default=False,
        help_text=_('Manage projects and perform administrative tasks.')
    )

    is_foreman = models.BooleanField(
        _('Foreman'), default=False,
        help_text=_('Manage workers in the field.')
    )

    is_laborer = models.BooleanField(
        _('Laborer'), default=True,
        help_text=_('Limited access in the field.')
    )

    is_accountant = models.BooleanField(
        _('Accountant'), default=False,
        help_text=_('Access to financial information.')
    )

    is_active = models.BooleanField(
        _('Active'), default=True,
        help_text=_('Must be enabled to allow worker access to the company. '
                    'Unchecking this will completely disable access for the worker '
                    'and you will not be able to assign tasks to them in the daily planner.')
    )

    can_track_time = models.BooleanField(
        _('Allowed to track their own time?'), default=False,
        help_text=_('Worker will be able to start and stop their own work timer. '
                    'Requires that "Time Tracking & Timesheets" is also enabled.')
    )

    @classmethod
    def grant_superuser_access(cls, user, company):
        """ Creates a temporary Access object dynamically to allow superusers access to any company. """
        assert user.is_superuser
        return cls(user=user, company=company, is_staff=True, is_active=True)

    @property
    def is_fake(self):
        """
        Check if this is a pseudo access object created by `grant_superuser_access`
        """
        return not self.pk

    @property
    def has_owner(self):
        return self.is_owner or self.user.is_superuser

    @property
    def has_staff(self):
        return self.is_staff or self.has_owner

    @property
    def has_foreman(self):
        return self.is_foreman or self.has_staff

    @property
    def has_laborer(self):
        return self.is_laborer or self.has_foreman

    @cached_property
    def todays_plans(self):
        return self.dailyplans.filter(day=date.today())

    @property
    def get_full_name(self):
        return self.user.get_full_name()

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def email(self):
        return self.user.email

    def __str__(self):
        return self.user.get_full_name()


class Contract(models.Model, RateType):
    name = models.CharField(_("Name"), blank=True, null=True, max_length=512)
    is_template = models.BooleanField(default=False)

    worker = models.ForeignKey("Worker", related_name="contracts", null=True, on_delete=models.CASCADE)

    requires_time_tracking = models.BooleanField(
        _('Time Tracking & Timesheets'), default=True,
        help_text=_('Enable this to allow workers time to be tracked and for timesheets to be generated.')
    )

    effective = models.DateField(
        _("Effective Date"), default=date.today, null=True,
        help_text=_('Date on which worker officially started working.')
    )

    rate = models.DecimalField(
        _("Rate"), max_digits=14, decimal_places=2,
        help_text=_("Workers' compensation amount in local currency")
    )
    rate_type = models.CharField(_("Rate Type"), max_length=128, choices=RateType.RATE_CHOICES, default=RateType.HOURLY)

    vacation = models.IntegerField(
        _("Vacation"), default=20*60,
        help_text=_("Vacation time (in hours) accumulated every month.")
    )

    work_start = models.TimeField(
        _("Work Start"), default=time(7, 00),
        help_text=_("Local time at which worker is expected to start working.")
    )

    morning_break_start = models.TimeField(
        _("Morning Break Start"), blank=True, null=True, default=time(9, 00),
        help_text=_("Start of morning break in local time.")
    )

    morning_break_end = models.TimeField(
        _("Morning Break End"), blank=True, null=True, default=time(9, 30),
        help_text=_("End of morning break in local time.")
    )

    lunch_break_start = models.TimeField(
        _("Lunch Break Start"), blank=True, null=True, default=time(12, 30),
        help_text=_("Start of lunch break in local time.")
    )

    lunch_break_end = models.TimeField(
        _("Lunch Break End"), blank=True, null=True, default=time(13, 00),
        help_text=_("End of lunch break in local time.")
    )

    work_end = models.TimeField(
        _("Work End"), default=time(16, 00),
        help_text=_("Local time at which worker is expected to finish working.")
    )

    abandoned_timer_penalty = models.IntegerField(
        _("Abandoned Timer Penalty"), default=-1*60,
        help_text=_("Penalty (in hours) applies to work day of a worker who manually "
                    "starts and then fails to stop their timer at the end of the day.")
    )

    @property
    def yearly_vacation_claim(self):
        if not self.effective:
            return 0
        elif self.effective.year == timezone.now().year:
            return (13 - self.effective.month) * self.vacation
        else:
            return 12 * self.vacation

    @property
    def morning_break(self) -> BreakSpan:
        if self.morning_break_start and self.morning_break_end:
            return BreakSpan(self.morning_break_start, self.morning_break_end)

    @property
    def lunch_break(self) -> BreakSpan:
        if self.lunch_break_start and self.lunch_break_end:
            return BreakSpan(self.lunch_break_start, self.lunch_break_end)

    @property
    def breaks(self):
        return [b for b in (self.morning_break, self.lunch_break) if b]


class LaborType(models.Model, RateType):
    name = models.CharField(_("Name"), max_length=512)
    rate = models.DecimalField(_("Rate"), max_digits=14, decimal_places=2)
    rate_type = models.CharField(_("Rate Type"), max_length=128, choices=RateType.RATE_CHOICES, default=RateType.HOURLY)
