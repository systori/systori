from .local import *

DATABASES['default'].update({
    'NAME': 'postgres',
    'USER': 'postgres',
    'HOST': 'localhost',
    'PORT': 5432
})

INSTALLED_APPS += (
    'django_extensions',
)
