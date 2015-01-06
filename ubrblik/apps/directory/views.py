from django.http import HttpResponseRedirect

from django.views.generic.base import View
from django.views.generic.list import ListView, MultipleObjectMixin
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy

from .models import Contact, ProjectContact
from .forms import ContactForm, ProjectContactForm

class DirectoryList(ListView):
    model = Contact

class ProjectContactSetBillable(SingleObjectMixin, View):
    model = ProjectContact
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_billable = True
        self.object.save()
        return HttpResponseRedirect(reverse('project.view', args=[self.object.project.id]))

class ProjectContactAdd(CreateView):
    model = ProjectContact
    template_name = 'directory/projectcontact_form_add.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectContactAdd, self).get_context_data(**kwargs)
        context['contact_list'] = Contact.objects.all()
        return context

    def get_form_kwargs(self):
        kwargs = super(ProjectContactAdd, self).get_form_kwargs()
        kwargs['instance'] = ProjectContact(project=self.request.project)
        return kwargs

    def get_success_url(self):
        return reverse('project.view', args=[self.request.project.id])

class ProjectContactCreate(CreateView):
    model = Contact
    form_class = ContactForm
    template_name = 'directory/projectcontact_form_create.html'
    def get_context_data(self, **kwargs):
        context = super(ProjectContactCreate, self).get_context_data(**kwargs)
        context['project_contact_form'] = ProjectContactForm
        return context

    def form_valid(self, form):
        response = super(ProjectContactCreate, self).form_valid(form)
        
        pc = ProjectContact(project=self.request.project, contact=self.object)
        association_form = ProjectContactForm(self.request.POST, instance=pc)
        association_form.save()

        return response

    def get_success_url(self):
        return reverse('project.view', args=[self.request.project.id])

class ProjectContactRemove(DeleteView):
    model = ProjectContact
    def get_success_url(self):
        return reverse('project.view', args=[self.request.project.id])

class ContactView(DetailView):
    model = Contact
    def get_context_data(self, **kwargs):
        context = super(ContactView, self).get_context_data(**kwargs)
        context['form'] = ContactForm(instance=self.object)
        return context

class ContactCreate(CreateView):
    model = Contact
    form_class = ContactForm
    success_url = reverse_lazy('directory')

class ContactUpdate(UpdateView):
    model = Contact
    form_class = ContactForm
    success_url = reverse_lazy('directory')

class ContactDelete(DeleteView):
    model = Contact
    success_url = reverse_lazy('directory')