""" Tests for `systori.apps.equipment.api` """
import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
)

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
        # A valid image file is required to pass the Form validation and do the upload
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
        os.remove(settings.MEDIA_ROOT + "/" + file_name)

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

    def test_can_delete_icon(self):
        """
        Expect equipment icon to be present and delete it
        """
        self.equipment.icon.save(
            "actual_name_in_db.jpg",
            SimpleUploadedFile("uploaded_name.jpg", b"", "image/jpeg"),
        )
        self.assertTrue(os.path.isfile(settings.MEDIA_ROOT + "/actual_name_in_db.jpg"))

        response = self.client.delete(
            f"/api/equipment/equipment/{self.equipment.pk}/icon/"
        )
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertFalse(os.path.isfile(settings.MEDIA_ROOT + "/actual_name_in_db.jpg"))
