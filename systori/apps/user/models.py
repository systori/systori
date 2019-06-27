from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.conf import settings

from allauth.account.models import EmailAddress


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, is_superuser, **extra_fields):
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(
            email=email, is_superuser=is_superuser, date_joined=now, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        return self._create_user(email, password, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    first_name = models.CharField(_("first name"), max_length=30, blank=False)
    last_name = models.CharField(_("last name"), max_length=30, blank=True)
    email = models.EmailField(_("email address"), unique=True, null=True, blank=True)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    language = models.CharField(
        _("language"), choices=settings.LANGUAGES, max_length=2, blank=True
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ("first_name",)

    @property
    def is_verified(self):
        return EmailAddress.objects.filter(user=self, verified=True).exists()

    def get_full_name(self):
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        return "{} <{}>".format(self.get_full_name(), self.email)


class AuthToken(models.Model):
    """
    Systori Auth Token
    """

    token = models.CharField(_("token"), max_length=40, primary_key=True)
    id = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="uid",
        on_delete=models.CASCADE,
        verbose_name=_("User"),
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    first_name = models.CharField(_("first name"), max_length=30, blank=False)
    last_name = models.CharField(_("last name"), max_length=30, blank=True)
    email = models.EmailField(_("email address"), unique=True, null=True, blank=True)
    pusher_key = models.CharField(
        "Pusher Api key", max_length=256, null=True, blank=True
    )

    class Meta:
        verbose_name = _("AuthToken")
        verbose_name_plural = _("AuthTokens")
