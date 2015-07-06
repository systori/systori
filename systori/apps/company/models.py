from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from tuath.models import AbstractSchema


class Company(AbstractSchema):
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Access', blank=True, related_name='companies')


class Access(models.Model):
    company = models.ForeignKey('Company', related_name="users_access")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="companies_access")

    class Meta:
        unique_together = ("company", "user")

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
                                                'active. Unselect this instead of deleting accounts.'))

    @property
    def has_staff(self):
        return self.is_staff or self.user.is_superuser

    @property
    def has_foreman(self):
        return self.is_foreman or self.has_staff

    @property
    def has_laborer(self):
        return self.is_laborer or self.has_foreman

