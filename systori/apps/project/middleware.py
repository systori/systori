from rest_framework.response import Response

from .models import Project


class ProjectMiddleware:
    def process_view(self, request, view, args, kwargs):
        if request.user.is_authenticated():
            if request.company:
                if 'project_pk' in kwargs:
                    request.project = Project.objects \
                        .prefetch_related("jobsites") \
                        .get(pk=kwargs['project_pk'])
                else:
                    request.project = Project.objects.template().get()

    def process_template_response(self, request, response):
        if request.user.is_authenticated():
            if request.company and getattr(response, 'context_data') is not None:
                if 'project' not in response.context_data and hasattr(request, 'project'):
                    response.context_data['project'] = request.project
        return response
