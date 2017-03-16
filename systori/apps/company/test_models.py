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

    def test_tracked_workers(self):
        company = CompanyFactory()  # type: Company
        worker1 = UserFactory(company=company).access.first()
        worker2 = UserFactory(company=company).access.first()
        worker1.contract.requires_time_tracking = False
        worker1.contract.save()
        workers = company.tracked_workers()
        self.assertNotIn(worker1, workers)
        self.assertIn(worker2, workers)
