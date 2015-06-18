from django.apps import AppConfig


class AccountingConfig(AppConfig):
    name = 'systori.apps.accounting'

    def ready(self):
        from . import receivers
