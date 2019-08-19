from systori.lib.testing import ClientTestCase
from django.utils.translation import ugettext as _
from datetime import date, timedelta
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

from systori.apps.main.factories import NoteFactory
from systori.apps.main.serializers import NoteSerializer

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
        note2 = NoteSerializer(NoteFactory(
            project=self.project, content_object=self.project, worker=self.worker
        )).data
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
            ["first_name", "last_name"], list(json[0]["workers"][0].keys())
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
        self.assertEqual(["first_name", "last_name", "projects"], list(json[0].keys()))
        self.assertEqual(["pk", "name", "day"], list(json[0]["projects"][0].keys()))
