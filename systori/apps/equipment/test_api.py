""" Tests for `systori.apps.equipment.api` """
import os

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND

from systori.lib.testing import ClientTestCase

from .factories import EquipmentFactory


class EquipmentApiTest(ClientTestCase):
    """ Tests for `systori.apps.equipment.api` """

    def setUp(self):
        super().setUp()
        self.equipment = EquipmentFactory()

    def test_can_set_icon(self):
        """
        Expect equipment icon to be updated/set and return it's url
        """
        test_image = "test_img.jpg"
        absulute_path = os.path.dirname(os.path.abspath(__file__)) + "/" + test_image
        with open(absulute_path, "rb") as icon:
            response = self.client.post(
                f"/api/equipment/equipment/{self.equipment.pk}/icon/",
                {"file": icon},
                format="multipart",
            )

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        file_name = response.json().rsplit("/", 1)[1]
        try:
            os.remove(f"./media/{file_name}")
        except FileNotFoundError as _:
            print(f"Manually remove the file /media/{file_name}")

    def test_can_get_icon(self):
        """
        Expect equipment icon to be present and return it's url
        """
        self.equipment.icon.save(
            "actual_name_in_db.jpg",
            SimpleUploadedFile("uploaded_name.jpg", b"", "image/jpeg"),
        )

        response = self.client.get(
            f"/api/equipment/equipment/{self.equipment.pk}/icon/"
        )

        self.assertEqual(response.status_code, HTTP_200_OK)

        # Cleanup
        os.remove(self.equipment.icon.path)

    def test_sends_404_for_no_icon(self):
        """
        Expect equipment icon to be NOT present and return HTTP status 404
        """

        response = self.client.get(
            f"/api/equipment/equipment/{self.equipment.pk}/icon/"
        )

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
