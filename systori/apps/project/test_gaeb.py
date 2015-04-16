import os.path
from django.conf import settings
from django.test import TestCase
from ..task.models import *
from .models import *

from ..task.test_models import create_task_data

from .gaeb_utils import *

class GaebImportTests(TestCase):

    def setUp(self):
        create_task_data(self)

    
    def test_import(self):
        file_path = os.path.join(settings.BASE_DIR, "apps/project/test_data/gaeb.x83")
        project = gaeb_import(file_path)
        print(project)
        self.assertEqual("7030 Herschelbad", project)
        #xml = open(´test_data...)
        #ok, and after this, i do ar