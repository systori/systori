from .models import Project, JobSite

class ProjectMiddleware:

    def process_view(self, request, view, args, kwargs):
        if 'project_pk' in kwargs:
            request.project = Project.objects.get(pk=kwargs['project_pk'])
        else:
            request.project = Project.objects.template().get()

    def process_template_response(self, request, response):
        if hasattr(response, 'context_data'):
            if 'project' not in response.context_data and hasattr(request, 'project'):
                response.context_data['project'] = request.project
        return response