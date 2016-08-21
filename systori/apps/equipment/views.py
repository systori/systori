from django.http import Http404
from django.views.generic import \
    ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse

from .models import Equipment, RefuelingStop, Maintenance
from .forms import EquipmentForm, RefuelingStopForm, MaintenanceForm


class EquipmentListView(ListView):
    model = Equipment
    template_name = "equipment/equipment_list.html"
    ordering = "name"

    def get_queryset(self, model=model):
        active_filter = self.kwargs['active_filter'] if 'active_filter' in self.kwargs else 'active'
        if 'active' in active_filter:
            return model.objects.filter(active=True)
        elif 'passive' in active_filter:
            return model.objects.filter(active=False)
        elif 'all' in active_filter:
            return model.objects.all()
        else:
            raise Http404


class EquipmentView(DetailView):
    model = Equipment

    def get_context_data(self, **kwargs):
        context = super(EquipmentView, self).get_context_data(**kwargs)
        context['refueling_stops'] = self.object.refuelingstop_set.order_by('-mileage')
        context['maintenances'] = self.object.maintenance_set.order_by('-mileage')
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


class RefuelingStopCreate(CreateView):
    model = RefuelingStop
    form_class = RefuelingStopForm
    template_name = 'equipment/equipment_form.html'

    def get_initial(self):
        return {'equipment': self.kwargs['pk']}

    def get_success_url(self):
        return reverse('equipment.view', args=(self.object.equipment.id,))


class RefuelingStopUpdate(UpdateView):
    model = RefuelingStop
    form_class = RefuelingStopForm
    template_name = 'equipment/equipment_form.html'

    def get_initial(self):
        return {'equipment': self.kwargs['equipment_pk']}

    # an updated Refueling Stop might change something in a younger Refueling Stop
    # this flag is to cascade the save method once to a younger object if present
    def form_valid(self, form):
        form.instance.cascade_save = True
        return super(RefuelingStopUpdate, self).form_valid(form)

    def get_success_url(self):
        return reverse('equipment.view', args=(self.object.equipment.id,))


class RefuelingStopDelete(DeleteView):
    model = RefuelingStop
    template_name = 'equipment/equipment_confirm_delete.html'

    def get_success_url(self):
        return reverse('equipment.view', args=(self.object.equipment.id,))


class MaintenanceCreate(CreateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = 'equipment/equipment_form.html'

    def get_initial(self):
        return {'equipment': self.kwargs['pk']}

    def get_success_url(self):
        return reverse('equipment.view', args=(self.object.equipment.id,))


class MaintenanceUpdate(UpdateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = 'equipment/equipment_form.html'

    def get_initial(self):
        return {'equipment': self.kwargs['equipment_pk']}

    def get_success_url(self):
        return reverse('equipment.view', args=(self.object.equipment.id,))


class MaintenanceDelete(DeleteView):
    model = Maintenance
    template_name = 'equipment/equipment_confirm_delete.html'

    def get_success_url(self):
        return reverse('equipment.view', args=(self.object.equipment.id,))
