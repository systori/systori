from .local import *

DATABASES['default'].update({
    'NAME': 'systori_local',
    'PORT': 5432
})
