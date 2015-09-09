from django.views import generic
from django.views.i18n import set_language
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .forms import *
from .forms import LanguageForm
from .models import *
from ..company.models import *


class SettingsView(generic.TemplateView):
    template_name = "user/settings.html"


class UserList(generic.ListView):
    model = Access
    template_name = 'user/user_list.html'

    def get_queryset(self):
        return Access.objects.\
            filter(company=self.request.company).\
            order_by('user__first_name').\
            prefetch_related('user')


class UserView(generic.DetailView):
    model = User


class UserFormRenderer:
    def render_forms(self, user_form, access_form):
        return self.render_to_response(self.get_context_data(
            user_form=user_form, access_form=access_form))

    def get_cleaned_forms(self, user=None, access=None):
        user_form = UserForm(self.request.POST, instance=user)
        user_form.full_clean()
        access_form = AccessForm(self.request.POST, instance=access)
        access_form.full_clean()
        return user_form, access_form


class UserAdd(generic.CreateView, UserFormRenderer):
    model = User
    success_url = reverse_lazy('users')

    def get(self, request, *args, **kwargs):
        self.object = None
        return self.render_forms(UserForm(), AccessForm())

    def post(self, request, *args, **kwargs):
        self.object = None

        user_form, access_form = self.get_cleaned_forms()

        # Before we do anything else make sure the forms are actually valid.
        if not user_form.is_valid() or not access_form.is_valid():
            return self.render_forms(user_form, access_form)

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

        elif Access.objects.filter(user=user, company=request.company).exists():
            # User exists and already has an access object for this company.
            user_form.add_error('email', _('This user is already a member of this company.'))
            return self.render_forms(user_form, access_form)

        # Finally create the access object for this user and company combination.
        access_form.instance.company = request.company
        access_form.instance.user = user
        access_form.save()

        return HttpResponseRedirect(self.success_url)


class UserUpdate(generic.UpdateView, UserFormRenderer):
    model = User
    success_url = reverse_lazy('users')

    def get(self, request, *args, **kwargs):
        user = self.object = self.get_object()
        access = Access.objects.get(user=user, company=request.company)
        return self.render_forms(UserForm(instance=user), AccessForm(instance=access))

    def post(self, request, *args, **kwargs):
        user = self.object = self.get_object()
        access = Access.objects.get(user=user, company=request.company)

        user_form, access_form = self.get_cleaned_forms(user, access)

        if user_form.is_valid() and access_form.is_valid():
            user_form.save()
            access_form.save()
            return HttpResponseRedirect(self.success_url)
        else:
            return self.render_forms(user_form, access_form)


class UserRemove(generic.DeleteView):
    model = Access


class UserGeneratePassword(generic.DetailView):
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


class SetLanguageView(generic.View):

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = LanguageForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
        return set_language(request)
