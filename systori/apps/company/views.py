from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy

from .models import Company, Access
from .forms import CompanyForm


class CompanyList(ListView):
    model = Company

    def get_queryset(self):
        return Company.objects.filter(users_access__user=self.request.user)


class CompanyCreate(CreateView):
    model = Company
    form_class = CompanyForm

    def form_valid(self, form):
        response = super(CompanyCreate, self).form_valid(form)
        Company.setup(self.object, self.request.user)
        return response

    def get_success_url(self):
        return self.object.url(self.request)


class CompanyUpdate(UpdateView):
    model = Company
    fields = ['name', 'is_active']
    success_url = reverse_lazy('companies')


class CompanyDelete(DeleteView):
    model = Company
    success_url = reverse_lazy('companies')
