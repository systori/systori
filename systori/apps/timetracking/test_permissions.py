from django.test import TestCase, RequestFactory
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ..company.factories import CompanyFactory
from ..user.factories import UserFactory
from .permissions import CanTrackTime


class CanTrackTimeView(APIView):
    permission_classes = (CanTrackTime,)

    def get(self, *args, **kwargs):
        return Response()


class CanTrackTimeTest(TestCase):

    def test_anonymous_user_cannot_get(self):
        request = RequestFactory().get('/')
        view_instance = CanTrackTimeView()
        response = view_instance.dispatch(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_canot_get_for_worker_who_cannot_track_time(self):
        user = UserFactory(company=CompanyFactory())
        worker = user.access.first()
        worker.can_track_time = False
        worker.save()
        request = RequestFactory().get('/')
        request.user = user
        request.worker = worker
        view_instance = CanTrackTimeView()
        response = view_instance.dispatch(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_get_for_worker_who_can_track_time(self):
        user = UserFactory(company=CompanyFactory())
        worker = user.access.first()
        worker.can_track_time = True
        worker.save()
        request = RequestFactory().get('/')
        request.user = user
        request.worker = worker
        view_instance = CanTrackTimeView()
        response = view_instance.dispatch(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
