from .common import *
from .dev import *

STATICFILES_DIRS += (
    ('dart', 'ubrblik/static/dart'),
)

DATABASES['default'].update({
    'NAME': 'ubrblik_local',
})
