import requests

from django.conf import settings
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

    def form_valid(self, form):
        response = super().form_valid(form)
        company, user = self.object, self.request.user
        event = {
            "event_name": "company-created",
            "created_at": company.created.timestamp(),
            "company_schema": company.schema,
            "company_name": company.name,
            "username": user.username,
            "email": user.email
        }
        headers = {
            'Authorization': 'Bearer '+settings.INTERCOM_ACCESS_TOKEN
        }
        if not settings.DEBUG and not settings.TESTING:
            try:
                requests.post('https://api.intercom.io/events', json=event, headers=headers)
            except:
                pass  # oh, well
        return response


class CompanyUpdate(UpdateView):
    model = Company
    form_class = CompanyForm
    success_url = reverse_lazy('companies')


class CompanyDelete(DeleteView):
    model = Company
    success_url = reverse_lazy('companies')
