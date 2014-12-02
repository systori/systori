from .common import *
from .dev import *

STATICFILES_DIRS += (
    ('coffee', 'ubrblik/static/coffee'),
)

DATABASES['default'].update({
    'NAME': 'ubrblik_local',
})
