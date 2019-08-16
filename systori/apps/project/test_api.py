from systori.lib.testing import ClientTestCase
from django.utils.translation import ugettext as _
from datetime import date, timedelta
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
