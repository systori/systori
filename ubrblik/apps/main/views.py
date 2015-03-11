from django.views.generic import View, TemplateView
from django.contrib.auth.views import login
from django_mobile import get_flavour
from django.conf import settings
from ..project.models import Project
from ..task.models import LineItem


class OfficeDashboard(TemplateView):
    template_name = "main/dashboard.html"
    def get_context_data(self, **kwargs):
        context = super(OfficeDashboard, self).get_context_data(**kwargs)
        context['flagged_lineitems'] = LineItem.objects.filter(is_flagged=True)
        projects = Project.objects.prefetch_related('jobs__taskgroups__tasks__taskinstances__lineitems')
        context['mapped_projects'] = projects.exclude(latitude=None).exclude(longitude=None).all()
        context['GOOGLE_MAPS_API_KEY'] = settings.GOOGLE_MAPS_API_KEY
        return context


class FieldDashboard(TemplateView):
    template_name = "field/dashboard.html"


class IndexView(View):
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated():
            if get_flavour() == 'full' and (user.is_staff or user.is_superuser):
                view = OfficeDashboard.as_view()
            else:
                view = FieldDashboard.as_view()
            return view(request, *args, **kwargs)
        else:
            return login(request, template_name="user/login.html")