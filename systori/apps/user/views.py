from django.views.generic import *
from django.core.urlresolvers import reverse, reverse_lazy

from .forms import *

from .models import *
from ..company.models import *


class SettingsView(TemplateView):
    template_name = "user/settings.html"


class UserList(ListView):
    model = User

    def get_queryset(self):
        return self.model.objects.\
            filter(companies__schema=self.request.session.get('company'))


class UserAdd(CreateView):
    model = User
    form_class = UserForm
    success_url = reverse_lazy('users')

    def form_valid(self, form):
        redirect = super(UserAdd, self).form_valid(form)
        company = Company.objects.get(schema=self.request.session.get('company'))
        Access.objects.create(user=self.object, company=company)
        return redirect


class UserView(DetailView):
    model = User


class UserUpdate(UpdateView):
    model = User
    form_class = UserForm
    success_url = reverse_lazy('users')


class UserRemove(DeleteView):
    model = Access
