from datetime import date
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from tuath.models import AbstractSchema

from systori.apps.project.models import Project
from systori.apps.accounting.workflow import create_chart_of_accounts


class Company(AbstractSchema):
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Access', blank=True, related_name='companies')

    def url(self, request):
        port = ''
        if ':' in request.META['HTTP_HOST']:
            port = ':'+request.META['HTTP_HOST'].split(':')[1]
        return request.scheme+'://'+self.schema+'.'+settings.SERVER_NAME+port

    @staticmethod
    def setup(company, owner):
        company.activate()
        Access.objects.create(company=company, user=owner, is_owner=True)
        Project.objects.create(name="Template Project", is_template=True)
        create_chart_of_accounts()

        return company


    @property
    def owner(self):
        return self.users_access.filter(is_owner=True).first()


class Access(models.Model):
    company = models.ForeignKey('Company', related_name="users_access")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="companies_access")

    class Meta:
        unique_together = ("company", "user")

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

    @classmethod
    def grant_superuser_access(cls, user, company):
        """ Creates a temporary Access object dynamically to allow superusers access to any company. """
        assert user.is_superuser
        return cls(user=user, company=company, is_staff=True, is_active=True)

    @property
    def has_owner(self):
        return self.is_owner or self.user.is_superuser

    @property
    def has_accountant(self):
        return self.is_accountant or self.has_owner

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

