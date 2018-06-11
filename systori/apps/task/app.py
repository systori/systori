from django.apps import AppConfig


class TaskConfig(AppConfig):
    name = "systori.apps.task"

    def ready(self):
        from . import receivers
