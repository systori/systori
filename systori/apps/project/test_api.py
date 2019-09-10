from systori.lib.testing import ClientTestCase
from django.utils.translation import ugettext as _
from datetime import date, timedelta
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from systori.apps.main.factories import NoteFactory
from systori.apps.main.serializers import NoteSerializer
from systori.apps.main.models import Note
from systori.apps.task.serializers import JobSerializer
from systori.apps.task.models import Job
from systori.apps.task.factories import JobFactory

from .api import get_week_by_day
from .models import TeamMember, EquipmentAssignment
from .factories import ProjectFactory, JobSiteFactory, DailyPlanFactory
from ..user.factories import UserFactory
from ..equipment.factories import EquipmentFactory


class ProjectApiTest(ClientTestCase):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.jobsite = JobSiteFactory(project=self.project)

    def test_projects_are_filtered(self):
        """
        Expect only Project which are is_template==False, so first object has pk==2 
        """
        response = self.client.get("/api/project/")
        self.assertEqual(response.json()["results"][0]["pk"], 2)

    def test_exists(self):
        response = self.client.get("/api/project/3/exists/")
        self.assertEqual(response.json()["name"], _("Project not found."))
        self.assertEqual(response.status_code, 206)

    def test_list_notes(self):
        note1 = NoteSerializer(
            NoteFactory(
                project=self.project, content_object=self.project, worker=self.worker
            )
        ).data
        note2 = NoteSerializer(
            NoteFactory(
                project=self.project, content_object=self.project, worker=self.worker
            )
        ).data
        response = self.client.get(f"/api/project/{self.project.pk}/notes/")
        self.assertEqual(response.status_code, HTTP_200_OK)
        json = response.json()
        self.assertDictContainsSubset(
            json[0],
            {
                "text": note1["text"],
                "created": note1["created"],
                "project": note1["project"],
                "worker": note1["worker"],
                "pk": note1["pk"],
                "html": note1["html"],
            },
        )
        self.assertDictContainsSubset(
            json[1],
            {
                "text": note2["text"],
                "created": note2["created"],
                "project": note2["project"],
                "worker": note2["worker"],
                "pk": note2["pk"],
                "html": note2["html"],
            },
        )

    def test_create_note(self):
        response = self.client.post(
            f"/api/project/{self.project.pk}/notes/", {"text": "This is a test note"}
        )

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        json = response.json()
        self.assertEqual(json["project"], self.project.pk)
        self.assertEqual(json["worker"], self.worker.pk)
        self.assertEqual(json["text"], "This is a test note")

    def test_update_note(self):
        note1 = NoteFactory(
            project=self.project, content_object=self.project, worker=self.worker
        )

        response = self.client.put(
            f"/api/project/{self.project.pk}/note/{note1.pk}/",
            {"text": "This is a test note"},
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        json = response.json()
        self.assertNotEqual(json["text"], note1.text)
        self.assertEqual(json["pk"], note1.pk)
        self.assertEqual(json["project"], self.project.pk)
        self.assertEqual(json["worker"], self.worker.pk)
        self.assertEqual(json["text"], "This is a test note")

    def test_get_note(self):
        note1 = NoteFactory(
            project=self.project, content_object=self.project, worker=self.worker
        )

        response = self.client.get(f"/api/project/{self.project.pk}/note/{note1.pk}/")

        self.assertEqual(response.status_code, HTTP_200_OK)
        json = response.json()
        self.assertEqual(json["text"], note1.text)
        self.assertEqual(json["pk"], note1.pk)
        self.assertEqual(json["project"], self.project.pk)
        self.assertEqual(json["worker"], self.worker.pk)

    def test_partial_update_note(self):
        note1 = NoteFactory(
            project=self.project, content_object=self.project, worker=self.worker
        )

        response = self.client.patch(
            f"/api/project/{self.project.pk}/note/{note1.pk}/",
            {"text": "This is a test note"},
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        json = response.json()
        self.assertNotEqual(json["text"], note1.text)
        self.assertEqual(json["pk"], note1.pk)
        self.assertEqual(json["project"], self.project.pk)
        self.assertEqual(json["worker"], self.worker.pk)
        self.assertEqual(json["text"], "This is a test note")

    def test_delete_note(self):
        note1 = NoteFactory(
            project=self.project, content_object=self.project, worker=self.worker
        )
        self.assertIsNotNone(Note.objects.get(pk=note1.pk))

        response = self.client.delete(
            f"/api/project/{self.project.pk}/note/{note1.pk}/"
        )

        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        with self.assertRaises(Note.DoesNotExist):
            Note.objects.get(pk=note1.pk)

    def test_list_jobs(self):
        job1 = JobFactory(project=self.project, description="job1 desc")

        job2 = JobFactory(project=self.project, description="job2 desc")

        response = self.client.get(f"/api/project/{self.project.pk}/jobs/")

        self.assertEqual(response.status_code, HTTP_200_OK)
        json = response.json()
        self.assertEqual(json[0]["name"], job1.name)
        self.assertEqual(json[0]["description"], "job1 desc")
        self.assertEqual(json[1]["name"], job2.name)
        self.assertEqual(json[1]["description"], "job2 desc")

    def test_create_job(self):
        response = self.client.post(
            f"/api/project/{self.project.pk}/jobs/",
            {"name": "This is a test job", "description": "this is a desc"},
        )

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        json = response.json()
        # self.assertEqual(json["project"], self.project.pk)
        self.assertEqual(json["name"], "This is a test job")
        self.assertEqual(json["description"], "this is a desc")

    def test_update_job(self):
        job1 = JobFactory(project=self.project)

        response = self.client.put(
            f"/api/project/{self.project.pk}/job/{job1.pk}/",
            {"description": "This is a test job"},
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        json = response.json()
        self.assertEqual(json["pk"], job1.pk)
        self.assertEqual(json["name"], job1.name)
        self.assertNotEqual(json["description"], job1.description)
        self.assertEqual(json["description"], "This is a test job")

    def test_get_job(self):
        job1 = JobFactory(project=self.project)

        response = self.client.get(f"/api/project/{self.project.pk}/job/{job1.pk}/")

        self.assertEqual(response.status_code, HTTP_200_OK)
        json = response.json()
        self.assertEqual(json["pk"], job1.pk)
        self.assertEqual(json["name"], job1.name)
        self.assertEqual(json["description"], job1.description)

    def test_partial_update_job(self):
        job1 = JobFactory(project=self.project)

        response = self.client.patch(
            f"/api/project/{self.project.pk}/job/{job1.pk}/",
            {"description": "This is a test job"},
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        json = response.json()
        self.assertEqual(json["pk"], job1.pk)
        self.assertEqual(json["name"], job1.name)
        self.assertNotEqual(json["description"], job1.description)
        self.assertEqual(json["description"], "This is a test job")

    def test_delete_job(self):
        job1 = JobFactory(project=self.project)
        self.assertIsNotNone(Job.objects.get(pk=job1.pk))

        response = self.client.delete(f"/api/project/{self.project.pk}/job/{job1.pk}/")

        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        with self.assertRaises(Job.DoesNotExist):
            Job.objects.get(pk=job1.pk)

    def test_search(self):
        response = self.client.put(
            "/api/project/search/", data={"query": self.project.name}
        )
        self.assertEqual(response.json()["projects"][0], self.project.pk)


class DailyPlanApiTest(ClientTestCase):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.jobsite = JobSiteFactory(project=self.project)
        self.user = UserFactory(company=self.company)
        self.worker = self.user.access.first()

    def test_week_by_day(self):
        # required format, apple TV client dependency
        beginning_of_week, end_of_week = get_week_by_day(date.today())
        for day in range(5):
            dp = DailyPlanFactory(
                jobsite=self.jobsite, day=beginning_of_week + timedelta(day)
            )
            TeamMember.objects.create(dailyplan=dp, worker=self.worker)
            e = EquipmentFactory()
            EquipmentAssignment.objects.create(dailyplan=dp, equipment=e)

        response = self.client.put(
            f"/api/dailyplan/week_by_day/", data={"selected_day": date.today()}
        )
        json = response.json()
        self.assertIsInstance(json, list)
        self.assertEqual(
            ["pk", "day", "jobsite", "workers", "equipment", "notes"],
            list(json[0].keys()),
        )
        self.assertEqual(
            [
                "first_name",
                "last_name",
                "email",
                "language",
                "is_verified",
                "get_full_name",
                "company",
                "user",
                "is_owner",
                "has_owner",
                "is_staff",
                "has_staff",
                "is_foreman",
                "has_foreman",
                "is_laborer",
                "has_laborer",
                "is_accountant",
                "is_active",
                "can_track_time",
                "is_fake",
            ],
            list(json[0]["workers"][0].keys()),
        )
        self.assertEqual(
            [
                "name",
                "project",
                "address",
                "city",
                "postal_code",
                "country",
                "latitude",
                "longitude",
            ],
            list(response.json()[0]["jobsite"].keys()),
        )
        self.assertEqual(
            [
                "id",
                "equipment_type",
                "active",
                "name",
                "manufacturer",
                "license_plate",
                "number_of_seats",
                "icon",
                "fuel",
                "last_refueling_stop",
            ],
            list(response.json()[0]["equipment"][0].keys()),
        )

    def test_week_by_day_pivot_workers(self):
        # required format, apple TV client dependency
        dp = DailyPlanFactory(jobsite=self.jobsite)
        TeamMember.objects.create(dailyplan=dp, worker=self.worker)
        response = self.client.put(
            f"/api/dailyplan/week_by_day_pivot_workers/",
            data={"selected_day": date.today()},
        )
        json = response.json()
        self.assertIsInstance(json, list)
        self.assertEqual(
            [
                "first_name",
                "last_name",
                "email",
                "language",
                "is_verified",
                "get_full_name",
                "company",
                "user",
                "is_owner",
                "has_owner",
                "is_staff",
                "has_staff",
                "is_foreman",
                "has_foreman",
                "is_laborer",
                "has_laborer",
                "is_accountant",
                "is_active",
                "can_track_time",
                "is_fake",
                "projects",
            ],
            list(json[0].keys()),
        )
        self.assertEqual(
            [
                "pk",
                "name",
                "description",
                "is_template",
                "structure",
                "notes",
                "phase",
                "state",
                "day",
            ],
            list(json[0]["projects"][0].keys()),
        )
