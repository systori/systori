import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'systori.settings.common')
from celery import Celery
from django.conf import settings
app = Celery('systori')
app.config_from_object(settings)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
