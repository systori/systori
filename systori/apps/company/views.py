from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Company
from .forms import CompanyForm


class CompanyList(ListView):
    model = Company


class CompanyCreate(CreateView):
    model = Company
    form_class = CompanyForm
    success_url = reverse_lazy('companies')


class CompanyUpdate(UpdateView):
    model = Company
    form_class = CompanyForm
    success_url = reverse_lazy('companies')


class CompanyDelete(DeleteView):
    model = Company
    success_url = reverse_lazy('companies')
