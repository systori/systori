from django.views.generic import View, TemplateView
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.i18n import set_language
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .forms import UserForm, WorkerForm, ContractForm, LanguageForm
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

    def render_forms(self, user_form, worker_form, contract_form):
        return self.render_to_response(self.get_context_data(
            user_form=user_form, worker_form=worker_form, contract_form=contract_form))

    def get_cleaned_forms(self, user=None, worker=None, contract=None, unique_email=True):
        user_form = UserForm(self.request.POST, instance=user, unique_email=unique_email)
        user_form.full_clean()
        worker_form = WorkerForm(self.request.POST, instance=worker)
        worker_form.full_clean()
        contract_form = ContractForm(self.request.POST, instance=contract)
        contract_form.full_clean()
        return user_form, worker_form, contract_form


class UserAdd(UserFormRenderer, CreateView):
    model = User
    success_url = reverse_lazy('users')

    def get(self, request, *args, **kwargs):
        self.object = None
        return self.render_forms(UserForm(), WorkerForm(), ContractForm())

    def post(self, request, *args, **kwargs):
        self.object = None

        user_form, worker_form, contract_form = self.get_cleaned_forms(unique_email=False)

        # Before we do anything else make sure the forms are actually valid.
        if not all([user_form.is_valid(), worker_form.is_valid(), contract_form.is_valid()]):
            return self.render_forms(user_form, worker_form, contract_form)

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
            # User exists and already has a worker object for this company.
            user_form.add_error('email', _('User with this email is already a member of this company.'))
            return self.render_forms(user_form, worker_form, contract_form)

        worker = worker_form.instance
        contract = contract_form.instance

        # Finally create the worker object for this user and company combination.
        worker.company = request.company
        worker.user = user
        worker_form.save()

        contract.worker = worker
        contract_form.save()

        worker.contract = contract
        worker.save()

        return HttpResponseRedirect(self.success_url)


class UserUpdate(UserFormRenderer, UpdateView):
    model = User
    success_url = reverse_lazy('users')

    def render_forms(self, user_form, worker_form, contract_form):
        return super().render_forms(
            None if user_form.instance.is_verified else user_form,
            worker_form, contract_form
        )

    def get(self, request, *args, **kwargs):
        user = self.object = self.get_object()
        worker = Worker.objects.get(user=user, company=request.company)
        return self.render_forms(
            UserForm(instance=user),
            WorkerForm(instance=worker),
            ContractForm(instance=worker.contract)
        )

    def post(self, request, *args, **kwargs):
        user = self.object = self.get_object()
        worker = Worker.objects.get(user=user, company=request.company)

        user_form, worker_form, contract_form = self.get_cleaned_forms(user, worker, worker.contract)

        forms = [user_form, worker_form, contract_form]
        if user.is_verified:
            forms.remove(user_form)

        if all(form.is_valid() for form in forms):
            for form in forms:
                form.save()
            return HttpResponseRedirect(self.success_url)
        else:
            return self.render_forms(user_form, worker_form, contract_form)


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
