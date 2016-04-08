from datetime import date
from django.test import TestCase
from django.test.client import MULTIPART_CONTENT
from django.conf import settings
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

    def setUp(self):
        create_task_data(self)
        self.client.login(username=self.user.email, password='open sesame')

    def client_get(self, path, data=None, follow=False, secure=False, **extra):
        extra['HTTP_HOST'] = self.company.schema + '.' + settings.SERVER_NAME
        return self.client.get(path, data, follow, secure, **extra)

    def client_post(self, path, data=None, content_type=MULTIPART_CONTENT,
                    follow=False, secure=False, **extra):
        extra['HTTP_HOST'] = self.company.schema + '.' + settings.SERVER_NAME
        return self.client.post(path, data, content_type, follow, secure, **extra)

    def test_complete_assigns_task_to_user_dailyplan(self):
        jobsite = JobSite.objects.create(project=self.project, name='a', address='a', city='a', postal_code='a')
        dailyplan = DailyPlan.objects.create(jobsite=jobsite)
        access, _ = Access.objects.get_or_create(user=self.user, company=self.company)

        self.client_post(
            reverse('field.dailyplan.task', args=['1', dailyplan.url_id, self.task.pk]),
            {'comment': 'test comment'}
        )
        self.task.refresh_from_db()
        self.assertFalse(self.task.dailyplans.filter(id=dailyplan.id).exists())

        self.client_post(
            reverse('field.dailyplan.task', args=['1', dailyplan.url_id, self.task.pk]),
            {'complete': 1}
        )
        self.task.refresh_from_db()
        self.assertFalse(self.task.dailyplans.filter(id=dailyplan.id).exists())

        TeamMember.objects.create(dailyplan=dailyplan, access=access)
        self.client_post(
            reverse('field.dailyplan.task', args=['1', dailyplan.url_id, self.task.pk]),
            {'complete': 2}
        )
        self.task.refresh_from_db()
        self.assertTrue(self.task.dailyplans.filter(id=dailyplan.id).exists())
