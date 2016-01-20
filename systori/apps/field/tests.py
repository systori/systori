from datetime import date
from django.test import TestCase
from django.core.urlresolvers import reverse

from ..project.models import TeamMember, DailyPlan, JobSite
from ..company.models import Access
from ..task.test_models import create_task_data
from .utils import find_next_workday


class TestDateCalculations(TestCase):
    def test_find_next_workday(self):
        self.assertEqual(date(2015, 3, 20), find_next_workday(date(2015, 3, 19)))
        self.assertEqual(date(2015, 3, 23), find_next_workday(date(2015, 3, 20)))
        self.assertEqual(date(2015, 3, 23), find_next_workday(date(2015, 3, 21)))
        self.assertEqual(date(2015, 3, 23), find_next_workday(date(2015, 3, 22)))
        self.assertEqual(date(2015, 3, 24), find_next_workday(date(2015, 3, 23)))


class TestFieldTaskView(TestCase):
    def test_complete_assigns_task_to_user_dailyplan(self):
        create_task_data(self)
        jobsite = JobSite.objects.create(project=self.project, name='a', address='a', city='a', postal_code='a')
        dailyplan = DailyPlan.objects.create(jobsite=jobsite)
        access, _ = Access.objects.get_or_create(user=self.user, company=self.company)

        self.client.login(username='lex@damoti.com', password='pass')

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
