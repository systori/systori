from django.views.generic import *
from .models import *
from .forms import *
from ..company.models import *


class SettingsView(TemplateView):
    template_name = "user/settings.html"


class UserList(ListView):
    model = User


class UserAdd(CreateView):
    model = User
    form_class = UserForm


class UserView(DetailView):
    model = User


class UserUpdate(UpdateView):
    model = User


class UserRemove(DeleteView):
    model = Access
