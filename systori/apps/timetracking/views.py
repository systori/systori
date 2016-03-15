import json

from django.shortcuts import redirect, get_object_or_404
from django.views.generic import View
from django.http import HttpResponse
from django.core.exceptions import ValidationError

from .models import Timer


class TimerView(View):

    def post(self, request):
        """
        Start a timer
        """
        try:
            Timer.launch(user=request.user)
        except ValidationError as exc:
            return HttpResponse(
                json.dumps({'errors': exc.messages}), 
                status=400, content_type='text/json'
            )
        return HttpResponse('')

    def put(self, request):
        """
        Stop a timer
        """
        timer = get_object_or_404(Timer.objects.get_running(), user=request.user)
        timer.stop()
        return HttpResponse('')

    def get(self, request):
        timer = get_object_or_404(Timer.objects.get_running(), user=request.user)
        return HttpResponse(timer.to_json(), content_type='text/json')


class HomeView(View):
    def get(self, request):
        pass
