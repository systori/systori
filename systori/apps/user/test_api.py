from systori.lib.testing import ClientTestCase
from ..user.factories import UserFactory


class ProjectApiTest(ClientTestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory(company=self.company, password="password")
        # self.user.password = "password"

    def test_user_gets_authenticated(self):
        """
        Expect retrieval of auth token and additional information
        """
        response = self.client.post("/api/token/", data={"username": self.user.email, "password": "password"})
        json = response.json()
        self.assertEqual(
            ['token', 'id', 'email', 'first_name', 'last_name', 'pusher_key'],
            list(json.keys())
        )
