from django.db import models
from django.conf import settings
from boardinghouse.models import AbstractSchema


class Company(AbstractSchema):
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Access', blank=True, related_name='companies')


class Access(models.Model):
    company = models.ForeignKey('Company', related_name="users_access")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="companies_access")

    is_enabled = models.BooleanField(default=True)

    is_employee = models.BooleanField(default=True)
    is_accountant = models.BooleanField(default=False)

