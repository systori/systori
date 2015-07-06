from django.views.generic import *
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from .forms import *

from .models import *
from ..company.models import *


class SettingsView(TemplateView):
    template_name = "user/settings.html"


class UserList(ListView):
    model = Access
    template_name = 'user/user_list.html'

    def get_queryset(self):
        return Access.objects.\
            filter(company=self.request.company).\
            order_by('user__first_name').\
            prefetch_related('user')


class UserAdd(CreateView):
    model = User
    success_url = reverse_lazy('users')

    def get(self, request, *args, **kwargs):
        self.object = None
        return self.render_forms(UserForm(), AccessForm())

    def post(self, request, *args, **kwargs):
        self.object = None

        user_form = UserForm(request.POST)
        user_form.full_clean()

        access_form = AccessForm(request.POST)
        access_form.full_clean()

        if not user_form.is_valid() or not access_form.is_valid():
            return self.render_forms(user_form, access_form)

        email = user_form.cleaned_data['email']

        user = None
        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                pass

        if not user:
            user = user_form.save()

        if not Access.objects.filter(user=user,company=request.company).exists():
            access_form.instance.company = request.company
            access_form.instance.user = user
            access_form.save()
        else:
            user_form.add_error('email', _('This user is already a member of this company.'))
            return self.render_forms(user_form, access_form)

        return HttpResponseRedirect(self.success_url)

    def render_forms(self, user_form, access_form):
        return self.render_to_response(self.get_context_data(
            user_form=user_form, access_form=access_form))


class UserView(DetailView):
    model = User


class UserUpdate(UpdateView):
    model = User
    success_url = reverse_lazy('users')

    def get(self, request, *args, **kwargs):
        user = self.object = self.get_object()
        access = Access.objects.get(user=user, company=request.company)
        return self.render_forms(UserForm(instance=user), AccessForm(instance=access))

    def post(self, request, *args, **kwargs):
        user = self.object = self.get_object()
        access = Access.objects.get(user=user, company=request.company)

        user_form = UserForm(request.POST, instance=user)
        user_form.full_clean()

        access_form = AccessForm(request.POST, instance=access)
        access_form.full_clean()

        if user_form.is_valid() and access_form.is_valid():
            user_form.save()
            access_form.save()
            return HttpResponseRedirect(self.success_url)

        else:
            return self.render_forms(user_form, access_form)

    def render_forms(self, user_form, access_form):
        return self.render_to_response(self.get_context_data(
            user_form=user_form, access_form=access_form))


class UserRemove(DeleteView):
    model = Access
