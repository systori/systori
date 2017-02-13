import pytz
from datetime import date, time
from decimal import Decimal
from typing import List
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from postgres_schema.models import AbstractSchema
from ..timetracking.utils import BreakSpan


class Company(AbstractSchema):
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Worker', blank=True, related_name='companies')

    def url(self, request):
        port = ''
        if ':' in request.META['HTTP_HOST']:
            port = ':'+request.META['HTTP_HOST'].split(':')[1]
        return request.scheme+'://'+self.schema+'.'+settings.SERVER_NAME+port

    def active_workers(self, **params):
        return self.workers.filter(is_active=True, **params).select_related('user')

    @property
    def breaks(self) -> List[BreakSpan]:
        """ TODO: store in database for each worker type/contract. """
        return [
            BreakSpan(time(9, 00), time(9, 30)),
            BreakSpan(time(12, 30), time(13, 00)),
        ]

    @property
    def holiday(self) -> int:
        """ TODO: store in database for each worker type/contract. """
        return int(2.5 * 8 * 60 * 60)

    @property
    def timezone(self) -> pytz.tzinfo.StaticTzInfo:
        """ TODO: store in database for each company. """
        # return pytz.timezone(self.timezone_name)
        return pytz.timezone(settings.TIME_ZONE)


class Worker(models.Model):
    company = models.ForeignKey('Company', related_name="workers", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="access", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("company", "user")

    # Permission flags

    is_owner = models.BooleanField(_('Owner'), default=False,
                                   help_text=_('Owner has full and unlimited Access to Systori.'))

    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                               'site.'))

    is_foreman = models.BooleanField(_('Foreman'), default=False,
                                     help_text=_('Foremen can manage laborers.'))

    is_laborer = models.BooleanField(_('Laborer'), default=True,
                                     help_text=_('Laborer has limited access to the system.'))

    is_accountant = models.BooleanField(_('accountant'), default=False)

    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts. '
                                                'This will remove user from any present and future daily plans.'))

    # Feature flags

    is_timetracking_enabled = models.BooleanField(_('timetracking enabled'), default=True,
                                               help_text=_('enable timetracking for this worker'))
    can_track_time = models.BooleanField(_('can track time'), default=False,
                                         help_text=_('allow this worker to start/stop work timer'))

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
