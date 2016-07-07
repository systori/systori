import json

from django.shortcuts import get_object_or_404
from django.views.generic import View
from django.http import HttpResponse, Http404
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Timer
from .utils import get_user_dashboard_report
from .permissions import HasStaffAccess
from .serializers import TimerStartSerializer, TimerSerializer


User = get_user_model()


class TimerView(views.APIView):
    permissions = (IsAuthenticated,)

    def post(self, request):
        """
        Start a timer
        """
        serializer = TimerStartSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response()

    def put(self, request):
        """
        Stop a timer
        """
        timer = get_object_or_404(Timer.objects.filter_running(), user=request.user)
        timer.stop()
        return Response()

    def get(self, request):
        timer = get_object_or_404(Timer.objects.filter_running(), user=request.user)
        return Response(timer.to_dict())


class ReportView(views.APIView):
    
    def get(self, request, year=None, month=None):
        return Response(TimerSerializer(get_user_dashboard_report(request.user), many=True).data)


class TimerAdminView(views.APIView):
    permissions = (HasStaffAccess,)

    def post(self, request, user_id):
        """
        Start user's timer
        """
        try:
            user = User.objects.get(pk=user_id)
            Timer.launch(user=user)
        except ValidationError as exc:
            return Response({'errors': exc.messages}, status=400)
        except User.ObjectDoesNotExist:
            raise Http404
        return Response()

    def put(self, request, user_id):
        """
        Stop user's timer
        """
        timer = get_object_or_404(Timer.objects.filter_running(), user__pk=user_id)
        timer.stop()
        return Response()

    def get(self, request, user_id):
        timer = get_object_or_404(Timer.objects.filter_running(), user__pk=user_id)
        return Response(timer.to_dict())
