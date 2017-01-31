from django.views.generic import View, TemplateView
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.i18n import set_language
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .forms import *
from .models import *
from ..company.models import Worker


class SettingsView(TemplateView):
    template_name = "user/settings.html"


class WorkerList(ListView):
    model = Worker
    template_name = 'user/user_list.html'
    context_object_name = 'access_list'

    def get_queryset(self):
        return Worker.objects.\
            filter(company=self.request.company).\
            order_by('user__first_name').\
            prefetch_related('user')


class UserView(DetailView):
    model = User


class UserFormRenderer:

    def get_form(self):
        return None

    def render_forms(self, user_form, worker_form, worker_flags_form):
        return self.render_to_response(self.get_context_data(
            user_form=user_form, worker_form=worker_form,
            worker_flags_form=worker_flags_form))

    def get_cleaned_forms(self, user=None, worker=None):
        user_form = UserForm(self.request.POST, instance=user)
        user_form.full_clean()
        worker_form = WorkerForm(self.request.POST, instance=worker)
        worker_form.full_clean()
        flags = worker.flags if worker else None
        worker_flags_form = WorkerFlagsForm(self.request.POST, instance=flags)
        worker_flags_form.full_clean()
        return user_form, worker_form, worker_flags_form


class UserAdd(UserFormRenderer, CreateView):
    model = User
    success_url = reverse_lazy('users')

    def get(self, request, *args, **kwargs):
        self.object = None
        return self.render_forms(UserForm(), WorkerForm(), WorkerFlagsForm())

    def post(self, request, *args, **kwargs):
        self.object = None

        user_form, worker_form, worker_flags_form = self.get_cleaned_forms()

        # Before we do anything else make sure the forms are actually valid.
        if not user_form.is_valid() or not worker_form.is_valid() or not worker_flags_form.is_valid():
            return self.render_forms(user_form, worker_form, worker_flags_form)

        email = user_form.cleaned_data['email']

        user = None
        if email:
            # Check if a user with this email already exists.
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                pass

        if not user:
            # User doesn't already exist, lets create them.
            user = user_form.save()

        elif Worker.objects.filter(user=user, company=request.company).exists():
            # User exists and already has an worker object for this company.
            user_form.add_error('email', _('This user is already a member of this company.'))
            return self.render_forms(user_form, worker_form, worker_flags_form)

        # Finally create the worker object for this user and company combination.
        worker_form.instance.company = request.company
        worker_form.instance.user = user
        worker = worker_form.save()

        worker_flags_form.instance.worker = worker
        worker_flags_form.instance.save()

        return HttpResponseRedirect(self.success_url)


class UserUpdate(UserFormRenderer, UpdateView):
    model = User
    success_url = reverse_lazy('users')

    def get(self, request, *args, **kwargs):
        user = self.object = self.get_object()
        worker = Worker.objects.get(user=user, company=request.company)
        return self.render_forms(
            UserForm(instance=user), WorkerForm(instance=worker),
            WorkerFlagsForm(instance=worker.flags))

    def post(self, request, *args, **kwargs):
        user = self.object = self.get_object()
        worker = Worker.objects.get(user=user, company=request.company)

        user_form, worker_form, worker_flags_form = self.get_cleaned_forms(user, worker)

        if user_form.is_valid() and worker_form.is_valid():
            user_form.save()
            worker_form.save()
            worker_flags_form.save()
            return HttpResponseRedirect(self.success_url)
        else:
            return self.render_forms(user_form, worker_form)


class WorkerRemove(DeleteView):
    model = Worker
    template_name = "user/access_confirm_delete.html"
    success_url = reverse_lazy('users')


class UserGeneratePassword(DetailView):
    model = User
    template_name = "user/password_generator.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        new_password = User.objects.make_random_password()
        self.object.set_password(new_password)
        self.object.save()
        context['new_password'] = new_password
        return self.render_to_response(context)


class SetLanguageView(View):

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = LanguageForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
        return set_language(request)
