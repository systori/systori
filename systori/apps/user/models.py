from datetime import date
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        return self._create_user(email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True,
                                 **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)

    email = models.EmailField(_('email address'), unique=True, null=True, blank=True)

    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                               'site.'))

    is_foreman = models.BooleanField(_('Foreman'), default=False,
                                     help_text=_('Foremen can manage laborers.'))

    is_laborer = models.BooleanField(_('Laborer'), default=True,
                                     help_text=_('Laborer has limited access to the system.'))

    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ('first_name',)

    @cached_property
    def todays_plans(self):
        return self.dailyplans.filter(day=date.today())

    @property
    def has_staff(self):
        return self.is_staff or self.is_superuser

    @property
    def has_foreman(self):
        return self.is_foreman or self.has_staff

    @property
    def has_laborer(self):
        return self.is_laborer or self.has_foreman

    @cached_property
    def visible_companies(self):
        return self.companies.active()

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)
