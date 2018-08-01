from django.urls import reverse
from systori.lib.testing import ClientTestCase
from django.utils.translation import ugettext as _
from .factories import ProjectFactory


class ProjectApiTest(ClientTestCase):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()

    def test_projects_are_filtered(self):
        """
        Expect only Project which are is_template==False, so first object has pk==2 
        """
        response = self.client.get("/api/v1/projects/")
        self.assertEqual(response.json()[0]["pk"], 2)

    def test_custom_action_exists(self):
        response = self.client.get("/api/v1/projects/3/exists/")
        self.assertEqual(response.json()["name"], _("Project not found."))
        self.assertEqual(response.status_code, 206)
