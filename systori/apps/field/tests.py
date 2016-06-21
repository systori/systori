import json
from datetime import date
from django.test import TestCase
from django.core.urlresolvers import reverse

from systori.lib.testing import SystoriTestCase
from ..project.models import TeamMember, DailyPlan, JobSite, EquipmentAssignment
from ..company.models import Access
from ..equipment.models import Equipment
from ..task.test_models import create_task_data
from .utils import find_next_workday


class TestDateCalculations(TestCase):
    def test_find_next_workday(self):
        self.assertEqual(date(2015, 3, 20), find_next_workday(date(2015, 3, 19)))
        self.assertEqual(date(2015, 3, 23), find_next_workday(date(2015, 3, 20)))
        self.assertEqual(date(2015, 3, 23), find_next_workday(date(2015, 3, 21)))
        self.assertEqual(date(2015, 3, 23), find_next_workday(date(2015, 3, 22)))
        self.assertEqual(date(2015, 3, 24), find_next_workday(date(2015, 3, 23)))


class TestFieldTaskView(SystoriTestCase):

    def setUp(self):
        create_task_data(self)
        self.client.login(username=self.user.email, password='open sesame')

    def test_complete_assigns_task_to_user_dailyplan(self):
        jobsite = JobSite.objects.create(project=self.project, name='a', address='a', city='a', postal_code='a')
        dailyplan = DailyPlan.objects.create(jobsite=jobsite)
        access, _ = Access.objects.get_or_create(user=self.user, company=self.company)

        self.client.post(
            reverse('field.dailyplan.task', args=['1', dailyplan.url_id, self.task.pk]),
            {'comment': 'test comment'}
        )
        self.task.refresh_from_db()
        self.assertFalse(self.task.dailyplans.filter(id=dailyplan.id).exists())

        self.client.post(
            reverse('field.dailyplan.task', args=['1', dailyplan.url_id, self.task.pk]),
            {'complete': 1}
        )
        self.task.refresh_from_db()
        self.assertFalse(self.task.dailyplans.filter(id=dailyplan.id).exists())

        TeamMember.objects.create(dailyplan=dailyplan, access=access)
        self.client.post(
            reverse('field.dailyplan.task', args=['1', dailyplan.url_id, self.task.pk]),
            {'complete': 2}
        )
        self.task.refresh_from_db()
        self.assertTrue(self.task.dailyplans.filter(id=dailyplan.id).exists())


class TestCutPaste(SystoriTestCase):

    def setUp(self):
        create_task_data(self)
        self.client.login(username=self.user.email, password='open sesame')

    def test_move_worker(self):
        jobsite = JobSite.objects.create(project=self.project, name='a', address='a', city='a', postal_code='a')
        dailyplan = DailyPlan.objects.create(jobsite=jobsite)
        access, _ = Access.objects.get_or_create(user=self.user, company=self.company)
        member = TeamMember.objects.create(dailyplan=dailyplan, access=access)

        jobsite2 = JobSite.objects.create(project=self.project, name='b', address='b', city='b', postal_code='b')
        dailyplan2 = DailyPlan.objects.create(jobsite=jobsite2)

        self.assertEqual(1, dailyplan.workers.count())
        self.assertEqual(0, dailyplan2.workers.count())
        self.client.post(
            reverse('field.dailyplan.paste', args=['1', dailyplan2.url_id]),
            json.dumps({'workers': [member.id]}),
            content_type='application/json'
        )
        self.assertEqual(0, dailyplan.workers.count())
        self.assertEqual(1, dailyplan2.workers.count())

    def test_move_equipment(self):
        jobsite = JobSite.objects.create(project=self.project, name='a', address='a', city='a', postal_code='a')
        dailyplan = DailyPlan.objects.create(jobsite=jobsite)
        equipment = Equipment.objects.create(name='truck')
        assignment = EquipmentAssignment.objects.create(dailyplan=dailyplan, equipment=equipment)

        jobsite2 = JobSite.objects.create(project=self.project, name='b', address='b', city='b', postal_code='b')
        dailyplan2 = DailyPlan.objects.create(jobsite=jobsite2)

        self.assertEqual(1, dailyplan.assigned_equipment.count())
        self.assertEqual(0, dailyplan2.assigned_equipment.count())
        self.client.post(
            reverse('field.dailyplan.paste', args=['1', dailyplan2.url_id]),
            json.dumps({'equipment': [assignment.id]}),
            content_type='application/json'
        )
        self.assertEqual(0, dailyplan.assigned_equipment.count())
        self.assertEqual(1, dailyplan2.assigned_equipment.count())
