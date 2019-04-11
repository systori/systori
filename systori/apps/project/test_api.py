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
        self.user = UserFactory(company=self.company)
        self.worker = self.user.access.first()

    def test_projects_are_filtered(self):
        """
        Expect only Project which are is_template==False, so first object has pk==2 
        """
        response = self.client.get("/api/projects/")
        self.assertEqual(response.json()[0]["pk"], 2)

    def test_custom_action_exists(self):
        response = self.client.get("/api/projects/3/exists/")
        self.assertEqual(response.json()["name"], _("Project not found."))
        self.assertEqual(response.status_code, 206)

    def test_WeekOfDailyPlansApiView(self):
        # required format, apple TV client dependency
        beginning_of_week, end_of_week = get_week_by_day(date.today())
        for day in range(5):
            dp = DailyPlanFactory(
                jobsite=self.jobsite, day=beginning_of_week + timedelta(day)
            )
            TeamMember.objects.create(dailyplan=dp, worker=self.worker)
            e = EquipmentFactory()
            EquipmentAssignment.objects.create(dailyplan=dp, equipment=e)

        response = self.client.get(f"/api/weekofdailyplans/{date.today()}/")
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
            ["name", "manufacturer", "number_of_seats", "license_plate"],
            list(response.json()[0]["equipment"][0].keys()),
        )

    def test_WeekOfPlannedWorkersApiView(self):
        # required format, apple TV client dependency
        dp = DailyPlanFactory(jobsite=self.jobsite)
        TeamMember.objects.create(dailyplan=dp, worker=self.worker)
        response = self.client.get(f"/api/weekofplannedworkers/{date.today()}/")
        json = response.json()
        self.assertIsInstance(json, list)
        self.assertEqual(["first_name", "last_name", "projects"], list(json[0].keys()))
        self.assertEqual(["pk", "name", "day"], list(json[0]["projects"][0].keys()))
