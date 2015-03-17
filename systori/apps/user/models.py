from datetime import date
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property


class User(AbstractUser):
    is_foreman = models.BooleanField(_('Foreman'), default=False,
        help_text=_('Foremen can manage laborers.'))
    is_laborer = models.BooleanField(_('Laborer'), default=True,
        help_text=_('Laborer has limited access to the system.'))

    @cached_property
    def todays_plans(self):
        return self.daily_plans.filter(day=date.today())

    class Meta:
        ordering = ('username',)