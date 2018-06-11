import json
from datetime import timedelta
from freezegun import freeze_time
from django.urls import reverse

from systori.lib.testing import ClientTestCase

from ..project.factories import ProjectFactory, JobSiteFactory
from ..task.factories import JobFactory, GroupFactory, TaskFactory

from ..project.models import (
    Project,
    TeamMember,
    DailyPlan,
    JobSite,
    EquipmentAssignment,
)
from ..equipment.models import Equipment
from ..user.factories import *
from .utils import find_next_workday, date


class TestDateCalculations(ClientTestCase):
    def test_find_next_workday(self):
        self.assertEqual(date(2015, 3, 20), find_next_workday(date(2015, 3, 19)))
        self.assertEqual(date(2015, 3, 23), find_next_workday(date(2015, 3, 20)))
        self.assertEqual(date(2015, 3, 23), find_next_workday(date(2015, 3, 21)))
        self.assertEqual(date(2015, 3, 23), find_next_workday(date(2015, 3, 22)))
        self.assertEqual(date(2015, 3, 24), find_next_workday(date(2015, 3, 23)))

    @freeze_time("2017-03-01")
    def test_selected_day_past_future(self):

        response = self.client.get(
            reverse(
                "field.planning",
                kwargs={"selected_day": date.today() - timedelta(days=1)},
            )
        )
        self.assertEqual(response.context["is_selected_past"], True)

        response = self.client.get(
            reverse("field.planning", kwargs={"selected_day": date.today()})
        )
        self.assertEqual(response.context["is_selected_today"], True)

        response = self.client.get(
            reverse(
                "field.planning",
                kwargs={"selected_day": date.today() + timedelta(days=1)},
            )
        )
        self.assertEqual(response.context["is_selected_future"], True)


class TestGroupTraversalView(ClientTestCase):
    def group_url(self, jobsite, dailyplan, *args):
        return reverse(
            "field.dailyplan.group", args=(jobsite.pk, dailyplan.url_id) + args
        )

    def test_job_with_tasks(self):
        project = ProjectFactory(structure="01.001")  # type: Project
        job = JobFactory(name="JobGroup", project=project)
        task = TaskFactory(
            name="Fence",
            group=job,
            qty=200,
            qty_equation="200",
            unit="m²",
            price=74.98,
            total=14996,
        )
        jobsite = JobSite.objects.create(
            project=project, name="a", address="a", city="a", postal_code="a"
        )
        dailyplan = DailyPlan.objects.create(jobsite=jobsite)

        # Project
        response = self.client.get(self.group_url(jobsite, dailyplan))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_parent_project"])
        self.assertFalse(response.context["is_parent_job"])
        self.assertTrue(response.context["parent_has_subgroups"])
        self.assertFalse(response.context["parent_has_tasks"])
        self.assertFalse(response.context["subgroups_have_subgroups"])
        self.assertTrue(response.context["subgroups_have_tasks"])
        self.assertEqual(response.context["groups"].count(), 1)
        self.assertIsNone(response.context["tasks"])

        # Job
        response = self.client.get(self.group_url(jobsite, dailyplan, job.pk))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["is_parent_project"])
        self.assertTrue(response.context["is_parent_job"])
        self.assertFalse(response.context["parent_has_subgroups"])
        self.assertTrue(response.context["parent_has_tasks"])
        self.assertFalse(response.context["subgroups_have_subgroups"])
        self.assertFalse(response.context["subgroups_have_tasks"])
        self.assertIsNone(response.context["groups"])
        self.assertEqual(response.context["tasks"].count(), 1)

    def test_job_with_groups_with_tasks(self):
        project = ProjectFactory(structure="01.01.01.01.001")
        job = JobFactory(name="JobGroup", project=project)
        group1 = GroupFactory(name="Group1", parent=job)
        group2 = GroupFactory(name="Group2", parent=group1)
        group3 = GroupFactory(name="Group3", parent=group2)
        task = TaskFactory(
            name="Fence",
            group=group3,
            qty=200,
            qty_equation="200",
            unit="m²",
            price=74.98,
            total=14996,
        )
        jobsite = JobSite.objects.create(
            project=project, name="a", address="a", city="a", postal_code="a"
        )
        dailyplan = DailyPlan.objects.create(jobsite=jobsite)

        # Project
        response = self.client.get(self.group_url(jobsite, dailyplan))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_parent_project"])
        self.assertFalse(response.context["is_parent_job"])
        self.assertTrue(response.context["parent_has_subgroups"])
        self.assertFalse(response.context["parent_has_tasks"])
        self.assertTrue(response.context["subgroups_have_subgroups"])
        self.assertFalse(response.context["subgroups_have_tasks"])
        self.assertEqual(response.context["groups"].count(), 1)
        self.assertIsNone(response.context["tasks"])

        # Job
        response = self.client.get(self.group_url(jobsite, dailyplan, job.pk))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["is_parent_project"])
        self.assertTrue(response.context["is_parent_job"])
        self.assertTrue(response.context["parent_has_subgroups"])
        self.assertFalse(response.context["parent_has_tasks"])
        self.assertTrue(response.context["subgroups_have_subgroups"])
        self.assertFalse(response.context["subgroups_have_tasks"])
        self.assertEqual(response.context["groups"].count(), 1)
        self.assertIsNone(response.context["tasks"])

        # Group 1
        response = self.client.get(self.group_url(jobsite, dailyplan, group1.pk))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["is_parent_project"])
        self.assertFalse(response.context["is_parent_job"])
        self.assertTrue(response.context["parent_has_subgroups"])
        self.assertFalse(response.context["parent_has_tasks"])
        self.assertTrue(response.context["subgroups_have_subgroups"])
        self.assertFalse(response.context["subgroups_have_tasks"])
        self.assertEqual(response.context["groups"].count(), 1)
        self.assertIsNone(response.context["tasks"])

        # Group 2
        response = self.client.get(self.group_url(jobsite, dailyplan, group2.pk))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["is_parent_project"])
        self.assertFalse(response.context["is_parent_job"])
        self.assertTrue(response.context["parent_has_subgroups"])
        self.assertFalse(response.context["parent_has_tasks"])
        self.assertFalse(response.context["subgroups_have_subgroups"])
        self.assertTrue(response.context["subgroups_have_tasks"])
        self.assertEqual(response.context["groups"].count(), 1)
        self.assertIsNone(response.context["tasks"])

        # Group 3
        response = self.client.get(self.group_url(jobsite, dailyplan, group3.pk))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["is_parent_project"])
        self.assertFalse(response.context["is_parent_job"])
        self.assertFalse(response.context["parent_has_subgroups"])
        self.assertTrue(response.context["parent_has_tasks"])
        self.assertFalse(response.context["subgroups_have_subgroups"])
        self.assertFalse(response.context["subgroups_have_tasks"])
        self.assertIsNone(response.context["groups"])
        self.assertEqual(response.context["tasks"].count(), 1)


class TestFieldTaskView(ClientTestCase):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.job = JobFactory(project=self.project)
        self.task = TaskFactory(name="the task", group=self.job)

    def test_complete_assigns_task_to_user_dailyplan(self):
        jobsite = JobSite.objects.create(
            project=self.project, name="a", address="a", city="a", postal_code="a"
        )
        dailyplan = DailyPlan.objects.create(jobsite=jobsite)
        access, _ = Worker.objects.get_or_create(user=self.user, company=self.company)

        self.client.post(
            reverse("field.dailyplan.task", args=["1", dailyplan.url_id, self.task.pk]),
            {"comment": "test comment"},
        )
        self.task.refresh_from_db()
        self.assertFalse(self.task.dailyplans.filter(id=dailyplan.id).exists())

        self.client.post(
            reverse("field.dailyplan.task", args=["1", dailyplan.url_id, self.task.pk]),
            {"complete": 1},
        )
        self.task.refresh_from_db()
        self.assertFalse(self.task.dailyplans.filter(id=dailyplan.id).exists())

        TeamMember.objects.create(dailyplan=dailyplan, worker=access)
        self.client.post(
            reverse("field.dailyplan.task", args=["1", dailyplan.url_id, self.task.pk]),
            {"complete": 2},
        )
        self.task.refresh_from_db()
        self.assertTrue(self.task.dailyplans.filter(id=dailyplan.id).exists())

    def test_add_and_remove_task_in_dailyplan(self):
        project = ProjectFactory(with_job=True)
        TaskFactory(name="the task", group=project.jobs.first())
        jobsite = JobSite.objects.create(
            project=project, name="a", address="a", city="a", postal_code="a"
        )
        dailyplan = DailyPlan.objects.create(jobsite=jobsite)
        self.assertEqual(dailyplan.tasks.count(), 0)
        response = self.client.get(
            reverse(
                "field.dailyplan.task.add", args=["1", dailyplan.url_id, self.task.pk]
            )
        )
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertEqual(dailyplan.tasks.first().name, "the task")
        response = self.client.get(
            reverse(
                "field.dailyplan.task.remove",
                args=["1", dailyplan.url_id, self.task.pk],
            )
        )
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertEqual(dailyplan.tasks.count(), 0)


class TestCutPaste(ClientTestCase):
    def test_move_worker(self):
        project = ProjectFactory()
        jobsite = JobSiteFactory(project=project)
        dailyplan = DailyPlan.objects.create(jobsite=jobsite)

        user1 = UserFactory(
            company=self.company, first_name="A", language="en", password=self.password
        )
        worker1 = user1.access.first()
        user2 = UserFactory(
            company=self.company, first_name="B", language="en", password=self.password
        )
        worker2 = user2.access.first()

        member1 = TeamMember.objects.create(dailyplan=dailyplan, worker=worker1)
        member2 = TeamMember.objects.create(dailyplan=dailyplan, worker=worker2)

        jobsite2 = JobSiteFactory(project=project)
        dailyplan2 = DailyPlan.objects.create(jobsite=jobsite2)

        self.assertEqual(2, dailyplan.members.count())
        self.assertEqual(member1, dailyplan.members.all()[0])
        self.assertEqual(member2, dailyplan.members.all()[1])
        self.assertEqual(0, dailyplan2.members.count())
        self.client.post(
            reverse("field.dailyplan.paste", args=["1", dailyplan2.url_id]),
            json.dumps({"workers": [member1.id]}),
            content_type="application/json",
        )
        self.assertEqual(1, dailyplan.members.count())
        self.assertEqual(member2, dailyplan.members.all()[0])
        self.assertEqual(1, dailyplan2.members.count())
        self.assertEqual(member1, dailyplan2.members.all()[0])

    def test_move_equipment(self):
        project = ProjectFactory()
        jobsite = JobSite.objects.create(
            project=project, name="a", address="a", city="a", postal_code="a"
        )
        dailyplan = DailyPlan.objects.create(jobsite=jobsite)
        equipment = Equipment.objects.create(name="truck")
        assignment = EquipmentAssignment.objects.create(
            dailyplan=dailyplan, equipment=equipment
        )

        jobsite2 = JobSite.objects.create(
            project=project, name="b", address="b", city="b", postal_code="b"
        )
        dailyplan2 = DailyPlan.objects.create(jobsite=jobsite2)

        self.assertEqual(1, dailyplan.assigned_equipment.count())
        self.assertEqual(0, dailyplan2.assigned_equipment.count())
        self.client.post(
            reverse("field.dailyplan.paste", args=["1", dailyplan2.url_id]),
            json.dumps({"equipment": [assignment.id]}),
            content_type="application/json",
        )
        self.assertEqual(0, dailyplan.assigned_equipment.count())
        self.assertEqual(1, dailyplan2.assigned_equipment.count())


class TestAssignEquipment(ClientTestCase):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.jobsite = JobSite.objects.create(
            project=self.project, name="a", address="a", city="a", postal_code="a"
        )
        self.dailyplan = DailyPlan.objects.create(jobsite=self.jobsite)
        self.equipment = Equipment.objects.create(name="truck")
        self.equipment2 = Equipment.objects.create(name="bulldozer")
        self.url = reverse(
            "field.dailyplan.assign-equipment",
            args=[self.jobsite.id, self.dailyplan.url_id],
        )

    def test_get_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("truck", response.content.decode("utf-8"))

    def test_no_assignments_deletes_dailyplan(self):
        self.assertTrue(DailyPlan.objects.filter(id=self.dailyplan.id).exists())
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertFalse(DailyPlan.objects.filter(id=self.dailyplan.id).exists())

    def test_equipment_assignment(self):
        self.assertEqual(0, self.dailyplan.assigned_equipment.count())
        response = self.client.post(self.url, {"equipment_list": [self.equipment.id]})
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertEqual(1, self.dailyplan.assigned_equipment.count())

    def test_equipment_unassignment(self):
        self.client.post(
            self.url, {"equipment_list": [self.equipment.id, self.equipment2.id]}
        )
        self.assertEqual(2, self.dailyplan.assigned_equipment.count())
        response = self.client.post(self.url, {"equipment_list": [self.equipment.id]})
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertEqual(1, self.dailyplan.assigned_equipment.count())


class TestAssignWorkers(ClientTestCase):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.jobsite = JobSite.objects.create(
            project=self.project, name="a", address="a", city="a", postal_code="a"
        )
        self.dailyplan = DailyPlan.objects.create(jobsite=self.jobsite)
        self.access, _ = Worker.objects.get_or_create(
            user=self.user, company=self.company
        )
        self.user2 = UserFactory(company=self.company)
        self.access2, _ = Worker.objects.get_or_create(
            user=self.user2, company=self.company
        )
        self.url = reverse(
            "field.dailyplan.assign-labor",
            args=[self.jobsite.id, self.dailyplan.url_id],
        )

    def test_get_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user.get_full_name(), response.content.decode("utf-8"))

    def test_labor_assignment(self):
        self.assertEqual(0, self.dailyplan.workers.count())
        response = self.client.post(self.url, {"workers": [self.access.id]})
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertEqual(1, self.dailyplan.workers.count())

    def test_labor_unassignment(self):
        self.client.post(self.url, {"workers": [self.access.id, self.access2.id]})
        self.assertEqual(2, self.dailyplan.workers.count())
        response = self.client.post(self.url, {"workers": [self.access.id]})
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertEqual(1, self.dailyplan.workers.count())


class TestCopyDailyPlans(ClientTestCase):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()

    def test_generate(self):
        today = date.today()
        yesterday = today - timedelta(days=1)
        jobsite = JobSite.objects.create(
            project=self.project, name="a", address="a", city="a", postal_code="a"
        )
        dailyplan = DailyPlan.objects.create(jobsite=jobsite, day=yesterday)
        access, _ = Worker.objects.get_or_create(user=self.user, company=self.company)
        TeamMember.objects.create(dailyplan=dailyplan, worker=access)
        equipment = Equipment.objects.create(name="truck")
        EquipmentAssignment.objects.create(dailyplan=dailyplan, equipment=equipment)
        self.assertEqual(1, DailyPlan.objects.count())
        self.assertEqual(0, DailyPlan.objects.filter(day=today).count())
        self.client.get(
            reverse(
                "field.planning.generate",
                kwargs={"selected_day": today, "source_day": yesterday},
            )
        )
        self.assertEqual(2, DailyPlan.objects.count())
        self.assertEqual(1, DailyPlan.objects.filter(day=today).count())


class TestDeleteDay(ClientTestCase):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()

    def test_generate_and_delete(self):
        today = date.today()
        jobsite = JobSite.objects.create(
            project=self.project, name="a", address="a", city="a", postal_code="a"
        )
        dailyplan = DailyPlan.objects.create(jobsite=jobsite, day=today)
        access, _ = Worker.objects.get_or_create(user=self.user, company=self.company)
        TeamMember.objects.create(dailyplan=dailyplan, worker=access)
        equipment = Equipment.objects.create(name="truck")
        EquipmentAssignment.objects.create(dailyplan=dailyplan, equipment=equipment)
        self.assertEqual(1, DailyPlan.objects.count())
        self.client.get(
            reverse("field.planning.delete-day", kwargs={"selected_day": today}),
            follow=True,
        )
        self.client.post(
            reverse("field.planning.delete-day", kwargs={"selected_day": today}),
            follow=True,
        )
        self.assertEqual(0, DailyPlan.objects.count())
