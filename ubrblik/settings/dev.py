from .common import *

DEBUG = True
TEMPLATE_DEBUG = True

DATABASES['default'].update({
    'NAME': 'ubrblik_dev'
})
