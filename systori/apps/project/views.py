from collections import OrderedDict
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import View, TemplateView, ListView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView, FormMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.contrib.postgres.search import SearchVector

from systori.lib.templatetags.customformatting import ubrdecimal
from .models import Project, JobSite
from .forms import ProjectCreateForm, ProjectImportForm, ProjectUpdateForm
from .forms import JobSiteForm
from ..task.models import Job, Group, ProgressReport
from ..document.models import Letterhead, DocumentTemplate, DocumentSettings
from ..accounting.models import create_account_for_job
from ..accounting.constants import TAX_RATE
from .gaeb_utils import gaeb_import


class ProjectList(ListView):
    queryset = Project._default_manager.all()

    phase_order = [
        "prospective",
        "tendering",
        "planning",
        "executing",
        "settlement",
        "warranty",
        "finished"
    ]

    def get(self, request, *args, **kwargs):
        project_groups = OrderedDict([(phase, []) for phase in self.phase_order])
        self.object_list = self.get_queryset().exclude(is_template=True)

        for project in self.object_list.order_by('id'):
            project_groups[project.phase].append(project)

        context = super(ProjectList, self).get_context_data(**kwargs)
        context['project_groups'] = project_groups
        context['phases'] = [phase for phase in Project.PHASE_CHOICES]

        return self.render_to_response(context)


class ProjectSearchApi(View):

    def get(self, request):
        query = Project.objects.without_template().prefetch_related('jobsites') \
                .prefetch_related('project_contacts__contact').prefetch_related('jobs').prefetch_related('invoices')

        project_filter = Q()
        searchable_paths = {}

        search_terms = [term for term in request.GET.get('search').split(' ')]
        for term in search_terms:
            searchable_paths[term] = Q(id__icontains=term) | Q(name__icontains=term) | Q(description__icontains=term) |\
                                     Q(jobsites__name__icontains=term) | \
                                     Q(jobsites__address__icontains=term) | \
                                     Q(jobsites__city__icontains=term) | \
                                     Q(jobs__name__icontains=term) | Q(jobs__description__icontains=term) | \
                                     Q(contacts__business__icontains=term) | \
                                     Q(contacts__first_name__icontains=term) | \
                                     Q(contacts__last_name__icontains=term) | \
                                     Q(contacts__address__icontains=term) | \
                                     Q(contacts__notes__icontains=term) | \
                                     Q(project_contacts__association__icontains=term) | \
                                     Q(invoices__invoice_no__icontains=term) | \
                                     Q(contacts__email__icontains=term)
        for key in searchable_paths.keys():
            project_filter &= searchable_paths[key]

        query = query.without_template().filter(project_filter).distinct()
        projects = [p.id for p in query]

        return JsonResponse({'projects': projects})


class ProjectView(DetailView):
    model = Project

    def get_context_data(self, **kwargs):
        context = super(ProjectView, self).get_context_data(**kwargs)
        context['proposals'] = self.object.proposals.prefetch_related('jobs__project').all()
        context['project_contacts'] = self.object.project_contacts.prefetch_related('contact').all()
        context['jobsites'] = self.object.jobsites.all()
        context['jobsites_count'] = len(context['jobsites'])
        context['project_has_billable_contact'] = self.object.has_billable_contact
        context['payments'] = self.object.payments.all()
        context['adjustments'] = self.object.adjustments.all()
        context['refunds'] = self.object.refunds.all()
        context['parent_invoices'] = self.object.invoices.filter(parent=None).prefetch_related('invoices').all()
        context['TAX_RATE_DISPLAY'] = '{}%'.format(ubrdecimal(TAX_RATE*100, 2))
        return context

    #def get_queryset(self):
    #    return super().get_queryset()\
    #        .prefetch_related('jobs__taskgroups__tasks__taskinstances__lineitems')


class ProjectCreate(CreateView):
    model = Project
    form_class = ProjectCreateForm

    def get_success_url(self):
        if 'save_goto_project' in self.request.POST:
            return reverse('project.view', args=[self.object.id])
        else:
            return reverse('projects')


class ProjectImport(FormView):
    form_class = ProjectImportForm
    template_name = "project/project_form_upload.html"

    def form_valid(self, form):
        self.object = gaeb_import(self.request.FILES['file'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('project.view', args=[self.object.id])  # otherwise this will fail


class ProjectUpdate(UpdateView):
    model = Project
    form_class = ProjectUpdateForm

    def get_success_url(self):
        if 'save_goto_project' in self.request.POST:
            return reverse('project.view', args=[self.object.id])
        else:
            return reverse('projects')


class ProjectDelete(DeleteView):
    model = Project
    success_url = reverse_lazy('projects')


class ProjectPlanning(DetailView):
    model = Project
    template_name = 'project/project_planning.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectPlanning, self).get_context_data(**kwargs)
        context['jobs'] = self.object.jobs.all()
        context['users'] = ["Fred", "Bob", "Frank", "John", "Jay", "Lex", "Marius"]
        return context


class ProjectProgress(DetailView):
    model = Project
    template_name = 'project/project_progress.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related('jobs__taskgroups__tasks__taskinstances__lineitems')


class ProjectManualPhaseTransition(SingleObjectMixin, View):
    model = Project

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        transition = None
        for t in self.object.get_available_user_phase_transitions(request.user):
            if t.name == kwargs['transition']:
                transition = t
                break

        if transition:
            getattr(self.object, transition.name)()
            self.object.save()

        return HttpResponseRedirect(reverse('project.view', args=[self.object.id]))


class ProjectManualStateTransition(SingleObjectMixin, View):
    model = Project

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        transition = None
        for t in self.object.get_available_user_state_transitions(request.user):
            if t.name == kwargs['transition']:
                transition = t
                break

        if transition:
            getattr(self.object, transition.name)()
            self.object.save()

        return HttpResponseRedirect(reverse('project.view', args=[self.object.id]))


class TemplatesView(TemplateView):
    template_name = 'main/templates.html'

    def get_context_data(self, **kwargs):
        context = super(TemplatesView, self).get_context_data(**kwargs)
        context['jobs'] = Project.objects.template().get().jobs.all()
        context['documents'] = DocumentTemplate.objects.all()
        context['document_settings'] = DocumentSettings.objects.all()
        context['letterheads'] = Letterhead.objects.all()
        return context


class JobSiteCreate(CreateView):
    model = JobSite
    form_class = JobSiteForm

    def get_form_kwargs(self):
        project = self.request.project
        address = project.jobsites.first()
        return {
            'instance': JobSite(project=project),
            'initial': {
                'address': address.address,
                'city': address.city,
                'postal_code': address.postal_code
            }
        }

    def get_success_url(self):
        return self.object.project.get_absolute_url()


class JobSiteUpdate(UpdateView):
    model = JobSite
    form_class = JobSiteForm

    def get_success_url(self):
        return self.object.project.get_absolute_url()


class JobSiteDelete(DeleteView):
    model = JobSite

    def get_success_url(self):
        return self.object.project.get_absolute_url()


class AllProjectsProgress(ListView):
    model = ProgressReport
    queryset = model.objects.prefetch_related('task__taskgroup__job__project').prefetch_related('worker__user')
    context_object_name = 'progressreport_list'
    paginate_by = 30
