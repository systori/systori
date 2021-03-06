import os
from drf_yasg.management.commands import generate_swagger
from django.utils import translation
from django.conf import settings

# TODO Can't override `generate_swagger` unless `main` app is moved before `drf_yasg` in `INSTALLED_APPS`
# See: https://docs.djangoproject.com/en/2.2/howto/custom-management-commands/#overriding-commands
class Command(generate_swagger.Command):
    help = "Generate swagger schema in schema.yaml"

    def handle(self, *args, **options):
        translation.activate("en")
        options["output_file"] = settings.SCHEMA_OUTPUT_FILEPATH
        options["overwrite"] = True
        options["api_url"] = "http://demo.sandbox.systori.com"
        super().handle(*args, **options)
