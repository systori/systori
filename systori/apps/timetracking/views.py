import json

from django.shortcuts import redirect, get_object_or_404
from django.views.generic import View
from django.http import HttpResponse
from django.core.exceptions import ValidationError

from .models import Timer
from .utils import get_report


class JsonResponse(HttpResponse):

    def __init__(self, content=b'', *args, **kwargs):
        kwargs['content_type'] = 'text/json'
        if content is not None and content != b'':
            content = json.dumps(content)
        super().__init__(content, *args, **kwargs)


class TimerView(View):

    def post(self, request):
        """
        Start a timer
        """
        try:
            Timer.launch(user=request.user)
        except ValidationError as exc:
            return JsonResponse({'errors': exc.messages}, status=400)
        return JsonResponse()

    def put(self, request):
        """
        Stop a timer
        """
        timer = get_object_or_404(Timer.objects.get_running(), user=request.user)
        timer.stop()
        return JsonResponse()

    def get(self, request):
        timer = get_object_or_404(Timer.objects.get_running(), user=request.user)
        return JsonResponse(timer.to_dict())


class ReportView(View):
    
    def get(self, request, year=None, month=None):
        return JsonResponse(list(get_report(request.user, year, month)))


class HomeView(View):
    def get(self, request):
        pass
