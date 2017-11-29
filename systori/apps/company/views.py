from raven.contrib.django.raven_compat.models import client

from django.conf import settings
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.mail import send_mail

from .models import Company
from .forms import CompanyForm


class CompanyList(TemplateView):
    template_name = 'company/company_list.html'


class CompanyCreate(CreateView):
    model = Company
    form_class = CompanyForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        company, user = self.object, self.request.user
        event = {
            "email": user.email,
            "schema": company.schema,
            "name": company.name
        }
        if not settings.TESTING:
            try:
                send_mail('new Company created',
                          'User {email} just created company {name} with schema {schema}'.format(**event),
                          'support@systori.com',
                          ['lex@damoti.com', 'marius@systori.com'])
            except:
                client.captureException()
        return response

    def get_success_url(self):
        return self.object.url(self.request)


class CompanyUpdate(UpdateView):
    model = Company
    form_class = CompanyForm
    success_url = reverse_lazy('companies')


class CompanyDelete(DeleteView):
    model = Company
    success_url = reverse_lazy('companies')
