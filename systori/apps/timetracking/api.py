from django.shortcuts import get_object_or_404
from rest_framework import views, serializers
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from systori.apps.timetracking.serializers import TimerSerializer, LatLongSerializer
from systori.apps.timetracking.models import Timer
from systori.apps.user.permissions import CanTrackTime


class TimerAPI(views.APIView):
    permissions = (CanTrackTime,)

    @staticmethod
    def post(request):
        """ Start a timer """
        latlong = LatLongSerializer(data=request.data)
        latlong.is_valid(raise_exception=True)
        lat, long = (
            latlong.validated_data["latitude"],
            latlong.validated_data["longitude"],
        )
        Timer.start(request.worker, starting_latitude=lat, starting_longitude=long)
        return Response()

    @staticmethod
    def put(request):
        """ Stop a timer """
        timer = get_object_or_404(Timer.objects.running(worker=request.worker))
        latlong = LatLongSerializer(data=request.data)
        latlong.is_valid(raise_exception=True)
        timer.ending_longitude = latlong.validated_data["longitude"]
        timer.ending_latitude = latlong.validated_data["latitude"]
        timer.stop()
        return Response()


urlpatterns = [url(r"^timer/$", login_required(TimerAPI.as_view()), name="api.timer")]


class TimerModelViewSet(ModelViewSet):
    queryset = Timer.objects.all()
    serializer_class = TimerSerializer
    permission_classes = (CanTrackTime,)
