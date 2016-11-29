import json

from django.shortcuts import get_object_or_404
from django.views.generic import View
from django.http import HttpResponse, Http404
from django.core.exceptions import ValidationError
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Timer
from ..company.models import Worker
from .utils import get_worker_dashboard_report
from ..user.permissions import HasStaffAccess
from .serializers import TimerStartSerializer, TimerStopSerializer, TimerSerializer


class TimerView(views.APIView):
    permissions = (IsAuthenticated,)

    def post(self, request):
        """
        Start a timer
        """
        serializer = TimerStartSerializer(data=request.data, context={'worker': request.worker})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response()

    def put(self, request):
        """
        Stop a timer
        """
        timer = get_object_or_404(Timer.objects.filter_running(), worker=request.worker)
        serializer = TimerStopSerializer(data=request.data, context={'worker': request.worker})
        serializer.is_valid(raise_exception=True)
        timer.end_longitude = serializer.validated_data['end_longitude']
        timer.end_latitude = serializer.validated_data['end_latitude']
        timer.stop()
        return Response()

    def get(self, request):
        timer = get_object_or_404(Timer.objects.filter_running(), worker=request.worker)
        return Response(timer.to_dict())


class ReportView(views.APIView):

    def get(self, request, year=None, month=None):
        return Response(TimerSerializer(get_worker_dashboard_report(request.worker), many=True).data)


class TimerAdminView(views.APIView):
    permissions = (HasStaffAccess,)

    def post(self, request, worker_id):
        """
        Start worker's timer
        """
        try:
            worker = Worker.objects.get(pk=worker_id)
            Timer.launch(worker=worker)
        except ValidationError as exc:
            return Response({'errors': exc.messages}, status=400)
        except Worker.ObjectDoesNotExist:
            raise Http404
        return Response()

    def put(self, request, worker_id):
        """
        Stop worker's timer
        """
        timer = get_object_or_404(Timer.objects.filter_running(), worker_id=worker_id)
        timer.stop()
        return Response()
