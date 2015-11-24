from collections import OrderedDict
from functools import reduce
from operator import or_
from django.http import HttpResponseRedirect
from django.views.generic import View, TemplateView, ListView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView, FormMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from systori.lib.templatetags.customformatting import ubrdecimal
from .models import Project, JobSite
from .forms import ProjectCreateForm, ProjectImportForm, ProjectUpdateForm, EntryFormSet
from .forms import JobSiteForm, FilterForm
from ..task.models import Job, TaskGroup
from ..document.models import Letterhead, DocumentTemplate, DocumentSettings
from ..accounting.utils import get_transactions_for_jobs
from ..accounting.models import Transaction, create_account_for_job
from ..accounting.constants import TAX_RATE
from .gaeb_utils import gaeb_import


class ProjectList(FormMixin, ListView):
    form_class = FilterForm
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

    def get_form_kwargs(self):
        return {
          'data': self.request.GET or None
        }

    def get_queryset(self, search_term=None, search_option=None):
        '''
        this function builds a query from multiple Q() objects to have a search behaviour like
        (TERM_A = project_name OR project_description OR ...)
        AND
        (TERM_B = project_name OR project_description OR ...)
        :param search_term: a single string with search terms, will get split by whitespace
        :param search_option: select where to search (project, jobs, projectContacts)
        :return: a query filter
        '''
        query = Project.objects.without_template().prefetch_related('jobsites')\
                .prefetch_related('project_contacts__contact')

        if search_term:
            project_filter = Q()
            searchable_paths = {}

            search_terms = search_term.split(' ')
            for term in search_terms:
                project_query = Q(name__icontains=term) | Q(description__icontains=term) | \
                                Q(jobsites__name__icontains=term) | \
                                Q(jobsites__address__icontains=term) | \
                                Q(jobsites__city__icontains=term)
                jobs_query =  Q(jobs__name__icontains=term) | Q(jobs__description__icontains=term) | \
                              Q(jobs__taskgroups__name__icontains=term) | \
                              Q(jobs__taskgroups__description__icontains=term) | \
                              Q(jobs__taskgroups__tasks__name__icontains=term) | \
                              Q(jobs__taskgroups__tasks__description__icontains=term) | \
                              Q(jobs__taskgroups__tasks__taskinstances__name__icontains=term) | \
                              Q(jobs__taskgroups__tasks__taskinstances__description__icontains=term) | \
                              Q(jobs__taskgroups__tasks__taskinstances__lineitems__name=term)
                contacts_query =  Q(contacts__business__icontains=term) | \
                                  Q(contacts__first_name__icontains=term) | \
                                  Q(contacts__last_name__icontains=term) | \
                                  Q(contacts__phone__icontains=term) | \
                                  Q(contacts__email__icontains=term) | \
                                  Q(contacts__website__icontains=term) | \
                                  Q(contacts__address__icontains=term) | \
                                  Q(contacts__notes__icontains=term) | \
                                  Q(project_contacts__association__icontains=term)
                                  #Q(project_contacts__notes__icontains=term)
                searchable_paths[term] = Q()

                if not search_option:
                    searchable_paths[term] |= project_query
                    searchable_paths[term] |= jobs_query
                    searchable_paths[term] |= contacts_query

                if 'contacts' in search_option:
                    searchable_paths[term] |= contacts_query

                if 'jobs' in search_option:
                    searchable_paths[term] |= jobs_query

                if 'jobs' in search_option and 'contacts' in search_option:
                    searchable_paths[term] |= contacts_query
                    searchable_paths[term] |= jobs_query

            for key in searchable_paths.keys():
                project_filter &= searchable_paths[key]

            return query.without_template().filter(project_filter).distinct()
        else:
            return query.without_template().all()


    def get(self, request, *args, **kwargs):

        project_groups = OrderedDict([(phase, []) for phase in self.phase_order])

        form = self.get_form(self.get_form_class())

        self.object_list = self.get_queryset().exclude(is_template=True)

        if form.is_valid():
            self.object_list = self.get_queryset(search_term=form.cleaned_data['search_term'],
                                                 search_option=form.cleaned_data['search_option'])
        else:
            self.object_list = self.get_queryset().without_template()

        if kwargs['phase_filter']:
            assert kwargs['phase_filter'] in self.phase_order
            self.object_list = self.object_list.filter(phase=kwargs['phase_filter'])
        else:
            #self.object_list = self.object_list.exclude(phase=Project.FINISHED)
            self.object_list = self.object_list

        for project in self.object_list:
            project_groups[project.phase].append(project)

        context = super(ProjectList, self).get_context_data(form=form, **kwargs)
        context['project_groups'] = project_groups

        return self.render_to_response(context)


class ProjectView(DetailView):
    model = Project

    def get_context_data(self, **kwargs):
        context = super(ProjectView, self).get_context_data(**kwargs)
        context['transactions'] = get_transactions_for_jobs(self.object.jobs.all())
        context['parent_invoices'] = self.object.invoices.filter(parent=None).prefetch_related('invoices').all()
        context['TAX_RATE_DISPLAY'] = '{}%'.format(ubrdecimal(TAX_RATE*100, 2))
        return context

    def get_queryset(self):
        queryset = super(ProjectView, self).get_queryset()
        return queryset.prefetch_related('jobs__taskgroups__tasks__taskinstances__lineitems')


class ProjectCreate(CreateView):
    model = Project
    form_class = ProjectCreateForm

    def form_valid(self, form):
        response = super(ProjectCreate, self).form_valid(form)

        job = Job.objects.create(job_code=1, name=_('Default'), project=self.object)
        job.account = create_account_for_job(job)
        job.save()

        TaskGroup.objects.create(name='', job=job)

        jobsite = JobSite()
        jobsite.project = self.object
        jobsite.name = _('Main Site')
        jobsite.address = form.cleaned_data['address']
        jobsite.city = form.cleaned_data['city']
        jobsite.postal_code = form.cleaned_data['postal_code']
        jobsite.save()

        return response

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
        return super(ProjectImport, self).form_valid(form)

    def get_success_url(self):
        return reverse('project.view', args=[self.object.id])  # otherwise this will fail


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
        queryset = super(ProjectProgress, self).get_queryset()
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


class TransactionEditor(TemplateView):
    template_name = 'project/transaction_editor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        transaction_ids = []
        for job in self.request.project.jobs.all():
            transaction_ids.extend(job.account.entries.all().values_list('transaction_id', flat=True))
        transaction_ids = list(set(transaction_ids))

        formsets = []
        for transaction in Transaction.objects.filter(id__in=transaction_ids).order_by('id'):
            formsets.append(EntryFormSet(instance=transaction))
        for formset in formsets:
            for form in formset:
                print(form)
        context['formsets'] = formsets

        return context

    def post(self, request, *args, **kwargs):
        formset = EntryFormSet(request.POST, instance=Transaction.objects.get(id=request.POST['transaction_id']))
        formset.save()
        return super().get(request, *args, **kwargs)
