from django.views.generic import TemplateView
from django.conf import settings
from ..project.models import Project
from ..task.models import LineItem
from ..document.models import DocumentTemplate

class SettingsView(TemplateView):
    template_name = "main/settings.html"

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        return context

class DashboardView(TemplateView):
    template_name = "main/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['flagged_lineitems'] = LineItem.objects.filter(is_flagged=True)
        context['mapped_projects'] = Project.objects.exclude(latitude=None).exclude(longitude=None).all()
        context['GOOGLE_MAPS_API_KEY'] = settings.GOOGLE_MAPS_API_KEY
        context['CURRENCY_SYMBOL'] = settings.CURRENCY_SYMBOL
        return context

class IndexView(TemplateView):
    template_name = "main/front_page.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            view = DashboardView.as_view()
            return view(request, *args, **kwargs)
        return super(IndexView, self).dispatch(request, *args, **kwargs)

class TemplatesView(TemplateView):
    template_name='main/templates.html'
    def get_context_data(self, **kwargs):
        context = super(TemplatesView, self).get_context_data(**kwargs)
        context['jobs'] = Project.objects.template().get().jobs.all()
        context['documents'] = DocumentTemplate.objects.all()
        return context