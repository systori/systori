import json
from datetime import timedelta
from django.test import TestCase
from django.core.urlresolvers import reverse

from systori.lib.testing import ClientTestCase

from ..project.factories import ProjectFactory
from ..task.factories import JobFactory, TaskFactory

from ..project.models import TeamMember, DailyPlan, JobSite, EquipmentAssignment
from ..equipment.models import Equipment
from ..user.factories import *
from .utils import find_next_workday, date


class TestDateCalculations(TestCase):
    def test_find_next_workday(self):
        self.assertEqual(date(2015, 3, 20), find_next_workday(date(2015, 3, 19)))
        self.assertEqual(date(2015, 3, 23), find_next_workday(date(2015, 3, 20)))
        self.assertEqual(date(2015, 3, 23), find_next_workday(date(2015, 3, 21)))
        self.assertEqual(date(2015, 3, 23), find_next_workday(date(2015, 3, 22)))
        self.assertEqual(date(2015, 3, 24), find_next_workday(date(2015, 3, 23)))


class TestFieldTaskView(ClientTestCase):

    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.job = JobFactory(project=self.project)
        self.task = TaskFactory(group=self.job)

    def test_complete_assigns_task_to_user_dailyplan(self):
        jobsite = JobSite.objects.create(project=self.project, name='a', address='a', city='a', postal_code='a')
        dailyplan = DailyPlan.objects.create(jobsite=jobsite)
        access, _ = Worker.objects.get_or_create(user=self.user, company=self.company)

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

        TeamMember.objects.create(dailyplan=dailyplan, worker=access)
        self.client.post(
            reverse('field.dailyplan.task', args=['1', dailyplan.url_id, self.task.pk]),
            {'complete': 2}
        )
        self.task.refresh_from_db()
        self.assertTrue(self.task.dailyplans.filter(id=dailyplan.id).exists())


class TestCutPaste(ClientTestCase):

    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()

    def test_move_worker(self):
        jobsite = JobSite.objects.create(project=self.project, name='a', address='a', city='a', postal_code='a')
        dailyplan = DailyPlan.objects.create(jobsite=jobsite)
        access, _ = Worker.objects.get_or_create(user=self.user, company=self.company)
        member = TeamMember.objects.create(dailyplan=dailyplan, worker=access)

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


class TestAssignEquipment(ClientTestCase):

    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.jobsite = JobSite.objects.create(project=self.project, name='a', address='a', city='a', postal_code='a')
        self.dailyplan = DailyPlan.objects.create(jobsite=self.jobsite)
        self.equipment = Equipment.objects.create(name='truck')
        self.equipment2 = Equipment.objects.create(name='bulldozer')
        self.url = reverse('field.dailyplan.assign-equipment', args=[self.jobsite.id, self.dailyplan.url_id])

    def test_get_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('truck', response.content.decode('utf-8'))

    def test_no_assignments_deletes_dailyplan(self):
        self.assertTrue(DailyPlan.objects.filter(id=self.dailyplan.id).exists())
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertFalse(DailyPlan.objects.filter(id=self.dailyplan.id).exists())

    def test_equipment_assignment(self):
        self.assertEqual(0, self.dailyplan.assigned_equipment.count())
        response = self.client.post(self.url, {'equipment_list': [self.equipment.id]})
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertEqual(1, self.dailyplan.assigned_equipment.count())

    def test_equipment_unassignment(self):
        self.client.post(self.url, {'equipment_list': [self.equipment.id, self.equipment2.id]})
        self.assertEqual(2, self.dailyplan.assigned_equipment.count())
        response = self.client.post(self.url, {'equipment_list': [self.equipment.id]})
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertEqual(1, self.dailyplan.assigned_equipment.count())


class TestAssignWorkers(ClientTestCase):

    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.jobsite = JobSite.objects.create(project=self.project, name='a', address='a', city='a', postal_code='a')
        self.dailyplan = DailyPlan.objects.create(jobsite=self.jobsite)
        self.access, _ = Worker.objects.get_or_create(user=self.user, company=self.company)
        self.user2 = UserFactory(company=self.company)
        self.access2, _ = Worker.objects.get_or_create(user=self.user2, company=self.company)
        self.url = reverse('field.dailyplan.assign-labor', args=[self.jobsite.id, self.dailyplan.url_id])

    def test_get_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user.get_full_name(), response.content.decode('utf-8'))

    def test_labor_assignment(self):
        self.assertEqual(0, self.dailyplan.workers.count())
        response = self.client.post(self.url, {'workers': [self.access.id]})
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertEqual(1, self.dailyplan.workers.count())

    def test_labor_unassignment(self):
        self.client.post(self.url, {'workers': [self.access.id, self.access2.id]})
        self.assertEqual(2, self.dailyplan.workers.count())
        response = self.client.post(self.url, {'workers': [self.access.id]})
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertEqual(1, self.dailyplan.workers.count())


class TestCopyDailyPlans(ClientTestCase):

    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()

    def test_generate(self):
        today = date.today()
        yesterday = today - timedelta(days=1)
        jobsite = JobSite.objects.create(project=self.project, name='a', address='a', city='a', postal_code='a')
        dailyplan = DailyPlan.objects.create(jobsite=jobsite, day=yesterday)
        access, _ = Worker.objects.get_or_create(user=self.user, company=self.company)
        TeamMember.objects.create(dailyplan=dailyplan, worker=access)
        equipment = Equipment.objects.create(name='truck')
        EquipmentAssignment.objects.create(dailyplan=dailyplan, equipment=equipment)
        self.assertEqual(1, DailyPlan.objects.count())
        self.assertEqual(0, DailyPlan.objects.filter(day=today).count())
        self.client.get(reverse('field.planning.generate', kwargs={'selected_day':today,'source_day':yesterday}))
        self.assertEqual(2, DailyPlan.objects.count())
        self.assertEqual(1, DailyPlan.objects.filter(day=today).count())


class TestDeleteDailyPlan(SystoriTestCase):

    def setUp(self):
        create_task_data(self)
        self.client.login(username=self.user.email, password='open sesame')

    def test_delete_dailyplan(self):
        today = date.today()
        jobsite = JobSite.objects.create(project=self.project, name='a', address='a', city='a', postal_code='a')
        dailyplan = DailyPlan.objects.create(jobsite=jobsite, day=today)
        access, _ = Access.objects.get_or_create(user=self.user, company=self.company)
        TeamMember.objects.create(dailyplan=dailyplan, access=access)
        equipment = Equipment.objects.create(name='chainsaw')
        EquipmentAssignment.objects.create(dailyplan=dailyplan, equipment=equipment)
        self.assertEqual(1, DailyPlan.objects.count())
        # first step the get request to trigger the confirmation page
        self.client.get(reverse('field.dailyplan.delete', kwargs={'jobsite_pk':jobsite.id,
                                                                  'dailyplan_url_id':dailyplan.url_id}), follow=True)
        # second step the post request to actually delete the object
        self.client.post(reverse('field.dailyplan.delete', kwargs={'jobsite_pk':jobsite.id,
                                                                  'dailyplan_url_id':dailyplan.url_id}), follow=True)
        self.assertEqual(0, DailyPlan.objects.count())
