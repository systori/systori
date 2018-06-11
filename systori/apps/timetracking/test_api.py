from datetime import timedelta
from urllib.parse import urlencode

from django.urls import reverse
from django.utils import timezone

from systori.lib.testing import ClientTestCase
from .models import Timer


class TimerViewTest(ClientTestCase):
    url = reverse("api.timer")

    def test_post(self):
        response = self.client.post(
            self.url, {"latitude": "52.5076", "longitude": "131.39043904"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Timer.objects.running(worker=self.worker).exists())

    def test_post_with_already_running_timer(self):
        Timer.start(self.worker)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_post_without_coordinates(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_put_with_short_timer(self):
        timer = Timer.start(self.worker)
        response = self.client.put(
            self.url,
            urlencode({"latitude": "52.5076", "longitude": "131.39043904"}),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(Timer.DoesNotExist):
            timer.refresh_from_db()

    def test_put(self):
        timer = Timer.objects.create(
            worker=self.worker, started=timezone.now() - timedelta(hours=1)
        )
        response = self.client.put(
            self.url,
            urlencode({"latitude": "52.5076", "longitude": "131.39043904"}),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(response.status_code, 200, response.data)
        timer.refresh_from_db()
        self.assertFalse(timer.is_running)
