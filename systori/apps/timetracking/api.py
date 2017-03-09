from django.shortcuts import get_object_or_404
from rest_framework import views
from rest_framework.response import Response

from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from .models import Timer
from .serializers import TimerStartSerializer, TimerStopSerializer
from .permissions import CanTrackTime


class TimerAPI(views.APIView):
    permissions = (CanTrackTime,)

    @staticmethod
    def post(request):
        """ Start a timer """
        serializer = TimerStartSerializer(data=request.data, context={'worker': request.worker})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response()

    @staticmethod
    def put(request):
        """ Stop a timer """
        timer = get_object_or_404(Timer.objects.filter_running(), worker=request.worker)
        serializer = TimerStopSerializer(data=request.data, context={'worker': request.worker})
        serializer.is_valid(raise_exception=True)
        timer.ending_longitude = serializer.validated_data['ending_longitude']
        timer.ending_latitude = serializer.validated_data['ending_latitude']
        timer.stop()
        return Response()

    @staticmethod
    def get(request):
        timer = get_object_or_404(Timer.objects.filter_running(), worker=request.worker)
        return Response({'duration': timer.running_duration})


urlpatterns = [
    url(r'^timer/$', login_required(TimerAPI.as_view()), name='api.timer'),
]
