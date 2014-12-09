from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import *

User = get_user_model()


def create_data(self):
    self.user = User.objects.create_user('lex', 'lex@damoti.com', 'pass')
    self.proj = Project.objects.create(name="my project")
    self.proj2 = Project.objects.create(name="my second project")