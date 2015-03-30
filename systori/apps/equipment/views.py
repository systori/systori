from django.views.generic import \
    ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy

from .models import Equipment
from .forms import EquipmentForm


class EquipmentListView(ListView):
    model = Equipment
    template_name = "equipment/equipment_list.html"


class EquipmentView(DetailView):
    model = Equipment

    def get_context_data(self, **kwargs):
        context = super(EquipmentView, self).get_context_data(**kwargs)
        context['form'] = EquipmentForm(instance=self.object)
        return context


class EquipmentCreate(CreateView):
    model = Equipment
    form_class = EquipmentForm
    success_url = reverse_lazy('equipment.list')


class EquipmentUpdate(UpdateView):
    model = Equipment
    form_class = EquipmentForm
    success_url = reverse_lazy('equipment.list')


class EquipmentDelete(DeleteView):
    model = Equipment
    success_url = reverse_lazy('equipment.list')
