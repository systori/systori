from django.test import TestCase
from .factories import CompanyFactory
from ..user.factories import UserFactory
from .models import Company, Worker, WorkerFlags


class CompanyTest(TestCase):

    def test_active_workers(self):
        company = CompanyFactory()
        user = UserFactory(company=company)
        worker = user.access.first()
        self.assertIn(worker, company.active_workers())
        Worker.objects.filter(user=user, company=company).update(is_active=False)
        self.assertNotIn(worker, company.active_workers())

    def test_active_workers_with_flags(self):
        company = CompanyFactory()
        user = UserFactory(company=company)
        worker = user.access.first()
        self.assertNotIn(worker, company.active_workers(can_track_time=True))
        flags = worker.flags
        flags.can_track_time = True
        flags.save()
        self.assertIn(worker, company.active_workers(can_track_time=True))
        # To check that the subsequent save doesn't cause exception
        worker.save()


class WorkerTest(TestCase):

    def test_flags_automatically_created(self):
        company = CompanyFactory()
        user = UserFactory(company=company)
        worker = user.access.first()
        self.assertEqual(worker.flags, WorkerFlags.objects.get(worker=worker))
