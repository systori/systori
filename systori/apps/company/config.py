from django.apps import AppConfig
from boardinghouse.apps import load_app_settings


class CompanyConfig(AppConfig):
    name = 'systori.apps.company'

    def ready(self):
        load_app_settings()
        monkey_patch_anonymous_user()


def monkey_patch_anonymous_user():
    from django.contrib.auth import models
    from .models import Company

    models.AnonymousUser.companies = Company.objects.none()
    models.AnonymousUser.visible_companies = Company.objects.none()
