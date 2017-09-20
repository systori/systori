from .local import *

DATABASES['default'].update({
    'NAME': 'systori_local',
    'USER': 'postgres',
    'HOST': 'localhost',
    'PORT': 5432
})
