from datetime import datetime, date
from freezegun import freeze_time
from django.test import TestCase
from django.utils import timezone

from .factories import CompanyFactory
from ..user.factories import UserFactory
from .models import Company, Worker

EST = timezone.get_fixed_timezone(-5)
NOW = datetime(2014, 12, 2, 17, 58, 28, 0, EST)  # birth of Systori


@freeze_time(NOW)
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

    def test_vacation_claim(self):
        company = CompanyFactory()
        worker1 = UserFactory(company=company).access.first()
        worker1.contract.effective = NOW.date()
        worker1.contract.save()
        self.assertEqual(worker1.contract.yearly_vacation_claim, 1200)
        worker1.contract.effective = date(2014, 1, 1)
        worker1.contract.save()
        self.assertEqual(worker1.contract.yearly_vacation_claim, 14400)
        worker1.contract.effective = None
        worker1.contract.save()
        self.assertEqual(worker1.contract.yearly_vacation_claim, 0)
