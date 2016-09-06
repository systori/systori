from django.test import TestCase
from .factories import CompanyFactory
from ..user.factories import UserFactory
from .models import Company, Worker


class CompanyTest(TestCase):

    def test_active_workers(self):
        company = CompanyFactory()
        user = UserFactory(company=company)
        worker = user.access.first()
        self.assertIn(worker, company.active_workers())
        Worker.objects.filter(user=user, company=company).update(is_active=False)
        self.assertNotIn(worker, company.active_workers())
