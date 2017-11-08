from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Company
from .forms import CompanyForm


class CompanyList(TemplateView):
    template_name = 'company/company_list.html'


class CompanyCreate(CreateView):
    model = Company
    form_class = CompanyForm
    success_url = reverse_lazy('companies')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class CompanyUpdate(UpdateView):
    model = Company
    form_class = CompanyForm
    success_url = reverse_lazy('companies')


class CompanyDelete(DeleteView):
    model = Company
    success_url = reverse_lazy('companies')
