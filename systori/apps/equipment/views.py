from django.views.generic import \
    ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy

from .models import Equipment, Vehicle
from .forms import VehicleForm


class EquipmentListView(ListView):
    model = Equipment
    template_name = "equipment/equipment_list.html"


class VehicleListView(ListView):
    model = Vehicle
    template_name = "equipment/vehicle_list.html"


class VehicleView(DetailView):
    model = Vehicle

    def get_context_data(self, **kwargs):
        context = super(VehicleView, self).get_context_data(**kwargs)
        context['form'] = VehicleForm(instance=self.object)
        return context


class VehicleCreate(CreateView):
    model = Vehicle
    form_class = VehicleForm
    success_url = reverse_lazy('vehicle.list')


class VehicleUpdate(UpdateView):
    model = Vehicle
    form_class = VehicleForm
    success_url = reverse_lazy('vehicle.list')


class VehicleDelete(DeleteView):
    model = Vehicle
    success_url = reverse_lazy('vehicle.list')
