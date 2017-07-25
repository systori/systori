from collections import OrderedDict
from datetime import date

from django.db.models import Q, Max, Min, Count, Sum
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View, TemplateView, ListView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView

from systori.lib.templatetags.customformatting import ubrdecimal
from .forms import JobSiteForm, GAEBImportForm
from .forms import ProjectCreateForm, ProjectUpdateForm
from .models import Project, JobSite, DailyPlan
from ..accounting.constants import TAX_RATE
from ..document.models import Letterhead, DocumentTemplate, DocumentSettings
from ..task.forms import JobCreateForm
from ..task.models import Job, ProgressReport


class ProjectList(ListView):
    model = Project

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

        context = super().get_context_data(**kwargs)
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

    def get_jobsites_and_activity(self):
        first_day = date.today()
        last_day = date(1970,1,1)
        jobsites = self.object.jobsites\
            .annotate(first_day=Min('dailyplans__day'), last_day=Max('dailyplans__day'))\
            .order_by('first_day')
        for site in jobsites:
            if site.first_day is not None:
                first_day = min(first_day, site.first_day)
                last_day = max(last_day, site.last_day)
            else:
                first_day, last_day = None, None

        return jobsites, first_day, last_day

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['jobs'] = self.object.jobs.with_totals().all()
        context['proposals'] = self.object.proposals.prefetch_related('jobs__project').all()
        context['project_contacts'] = self.object.project_contacts.prefetch_related('contact').all()

        context['jobsites'],\
        context['activity_first_day'],\
        context['activity_last_day'] = self.get_jobsites_and_activity()

        context['jobsites_count'] = len(context['jobsites'])
        context['project_has_billable_contact'] = self.object.has_billable_contact
        context['payments'] = self.object.payments.all()
        context['adjustments'] = self.object.adjustments.all()
        context['refunds'] = self.object.refunds.all()
        context['parent_invoices'] = self.object.invoices.filter(parent=None).prefetch_related('invoices').all()
        context['TAX_RATE_DISPLAY'] = '{}%'.format(ubrdecimal(TAX_RATE*100, 2))
        return context

    def get_queryset(self):
        return super().get_queryset().with_totals()


class ProjectCreate(CreateView):
    model = Project
    form_class = ProjectCreateForm

    def get_jobsite_form(self):
        if self.request.company.is_jobsite_required:
            kwargs = {'initial': {'name': _('Main Site')}}
            if self.request.method == 'POST':
                kwargs['data'] = self.request.POST
            return JobSiteForm(prefix='jobsite', **kwargs)

    def get_context_data(self, **kwargs):
        if 'jobsite_form' not in kwargs:
            kwargs['jobsite_form'] = self.get_jobsite_form()
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        jobsite_form = self.get_jobsite_form()
        if form.is_valid() and (not jobsite_form or jobsite_form.is_valid()):
            return self.forms_valid(form, jobsite_form)
        self.object = None
        return self.render_to_response(self.get_context_data(
            form=form, jobsite_form=jobsite_form
        ))

    def forms_valid(self, form, jobsite_form):
        project = form.save()

        if jobsite_form:
            jobsite_form.instance.project = project
            jobsite_form.save()

        JobCreateForm({
            'name': project.name,
        }, instance=Job(project=project)).save()

        if 'save_goto_project' in self.request.POST:
            redirect = reverse('project.view', args=[project.id])
        else:
            redirect = reverse('projects')

        return HttpResponseRedirect(redirect)


class GAEBImportView(FormView):
    form_class = GAEBImportForm
    template_name = "project/gaeb_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'project_pk' in self.kwargs:
            kwargs['project'] = self.request.project
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            project = form.save()
            return HttpResponseRedirect(project.get_absolute_url())
        return self.form_invalid(form)


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


class ProjectProgress(DetailView):
    model = Project
    template_name = 'project/project_progress.html'

    def get_summary(self, jobs):
        summary = {}
        summary['estimate'] = []
        summary['progress'] = []
        summary['percent'] = []
        summary['estimate'].append(self.object.estimate)
        summary['progress'].append(self.object.progress)
        summary['percent'].append(self.object.progress_percent)
        for job in jobs:
            summary['estimate'].append(job.estimate)
            summary['progress'].append(job.progress)
            summary['percent'].append(job.progress_percent)
        return summary

    def get_names(self, jobs):
        names = []
        names.append(self.object.name)
        names.extend([job.name for job in jobs])
        return names

    def get_queryset(self):
        return super().get_queryset().with_totals()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        jobs = self.object.jobs.with_hierarchy(self.object).with_totals()
        context['jobs'] = jobs
        context['summary'] = self.get_summary(jobs)
        context['names'] = self.get_names(jobs)
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


class ProjectDailyPlansView(TemplateView):
    model = DailyPlan
    template_name = "project/project_dailyplans.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, id=kwargs['project_pk'])
        jobsites = project.jobsites.prefetch_related('dailyplans__workers').all()
        workers = {}
        context['dailyplans'] = []
        for jobsite in jobsites:
            for dailyplan in jobsite.dailyplans.all():
                context['dailyplans'].append(dailyplan)
                dailyplan.worker_count = 0
                for worker in dailyplan.workers.all():
                  workers.setdefault(worker.get_full_name, 0)
                  workers[worker.get_full_name] += 1
                  dailyplan.worker_count += 1
        context['workers_summary'] = sorted(workers.items(), key=lambda x: x[1], reverse=True)
        return context


class TemplatesView(TemplateView):
    template_name = 'main/templates.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['jobs'] = Project.objects.template().get().jobs.all()
        context['documents'] = DocumentTemplate.objects.all()
        context['document_settings'] = DocumentSettings.objects.all()
        context['letterheads'] = Letterhead.objects.all()
        return context


class JobSiteCreate(CreateView):
    model = JobSite
    form_class = JobSiteForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        project = self.request.project
        previous = project.jobsites.first()
        if previous:
            previous.id = None
            previous.name = ''
            kwargs['instance'] = previous
        else:
            kwargs['instance'] = self.model(project=project)
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


class AllProjectsProgress(ListView):
    model = ProgressReport
    queryset = model.objects.prefetch_related('worker__user')
    context_object_name = 'progressreport_list'
    paginate_by = 30
