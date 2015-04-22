from django.http import HttpResponseRedirect
from django.views.generic import View, TemplateView, ListView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from .models import Project, JobSite
from .forms import ProjectCreateForm, ProjectImportForm, ProjectUpdateForm
from .forms import JobSiteForm
from ..task.models import Job, TaskGroup, Task
from ..directory.models import ProjectContact
from ..document.models import Invoice, DocumentTemplate
from ..accounting.models import create_account_for_project
from ..accounting.utils import get_transactions_table
from .gaeb_utils import gaeb_import


class ProjectList(ListView):
    model = Project

    def get_queryset(self):
        return self.model.objects.without_template()


class ProjectView(DetailView):
    model = Project

    def get_context_data(self, **kwargs):
        context = super(ProjectView, self).get_context_data(**kwargs)
        context['transactions'] = get_transactions_table(self.object)
        return context

    def get_queryset(self):
        queryset = super(ProjectView, self).get_queryset()
        return queryset.prefetch_related('jobs__taskgroups__tasks__taskinstances__lineitems')


class ProjectCreate(CreateView):
    model = Project
    form_class = ProjectCreateForm

    def form_valid(self, form):
        response = super(ProjectCreate, self).form_valid(form)

        TaskGroup.objects.create(name='',
          job=Job.objects.create(name=_('Default'), project=self.object)
        )

        jobsite = JobSite()
        jobsite.project = self.object
        jobsite.name = _('Main Site')
        jobsite.address = form.cleaned_data['address']
        jobsite.city = form.cleaned_data['city']
        jobsite.postal_code = form.cleaned_data['postal_code']
        jobsite.save()

        self.object.account = create_account_for_project(self.object)
        self.object.save()

        return response

    def get_success_url(self):
        return reverse('project.view', args=[self.object.id])


class ProjectImport(FormView):
    """ Import Function to import Gaeb X83 proposal request files. based on lxml objectify"""
    form_class = ProjectImportForm
    template_name = "project/project_form_upload.html"
    
    def form_valid(self, form):
        self.object = gaeb_import(self.request.FILES['file'])
        return super(ProjectImport, self).form_valid(form) # <- this will call get_success_url(), so self.object h
    # has to already be set before hand
    
    def get_success_url(self):
        return reverse('project.view', args=[self.object.id]) # otherwise this will fail


class ProjectUpdate(UpdateView):
    model = Project
    form_class = ProjectUpdateForm

    def get_success_url(self):
        return reverse('project.view', args=[self.object.id])


class ProjectDelete(DeleteView):
    model = Project
    success_url = reverse_lazy('projects')


class ProjectPlanning(DetailView):
    model = Project
    template_name='project/project_planning.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectPlanning, self).get_context_data(**kwargs)
        context['jobs'] = self.object.jobs.all()
        context['users'] = ["Fred", "Bob", "Frank", "John", "Jay", "Lex", "Marius"]
        return context


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




class TemplatesView(TemplateView):
    template_name='main/templates.html'

    def get_context_data(self, **kwargs):
        context = super(TemplatesView, self).get_context_data(**kwargs)
        context['jobs'] = Project.objects.template().get().jobs.all()
        context['documents'] = DocumentTemplate.objects.all()
        return context


class JobSiteCreate(CreateView):
    model = JobSite
    form_class = JobSiteForm

    def get_form_kwargs(self):
        kwargs = super(JobSiteCreate, self).get_form_kwargs()

        kwargs['instance'] = JobSite(project=self.request.project)

        address = self.request.project.jobsites.first()
        kwargs['initial'].update({
            'address': address.address,
            'city': address.city,
            'postal_code': address.postal_code
        })

        return kwargs

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
