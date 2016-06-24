import json
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

from .factories import CompanyFactory
from ..user.factories import UserFactory
from .models import Company, Access


class CompanyTest(TestCase):

    def test_active_users(self):
        company = CompanyFactory()
        user = UserFactory(company=company)
        self.assertIn(user, company.active_users())
        Access.objects.filter(user=user, company=company).update(is_active=False)
        self.assertNotIn(user, company.active_users())
