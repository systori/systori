from django.apps import AppConfig


class ProjectConfig(AppConfig):
    name = "systori.apps.project"

    def ready(self):
        from . import receivers
