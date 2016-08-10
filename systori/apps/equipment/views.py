from django.views.generic import \
    ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse

from .models import Equipment, RefuelingStop
from .forms import EquipmentForm, RefuelingStopForm


class EquipmentListView(ListView):
    model = Equipment
    template_name = "equipment/equipment_list.html"


class EquipmentView(DetailView):
    model = Equipment

    def get_context_data(self, **kwargs):
        context = super(EquipmentView, self).get_context_data(**kwargs)
        context['form'] = EquipmentForm(instance=self.object)
        context['refueling_stops'] = RefuelingStop.objects.filter(equipment=self.object.id).order_by('-datetime')
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
    #success_url = reverse_lazy('equipment.detail')
    template_name = 'equipment/equipment_form.html'

    def get_form_kwargs(self):
        kwargs = super(RefuelingStopCreate, self).get_form_kwargs()

        equipment = Equipment(id=int(self.kwargs['pk']))
        kwargs['initial'].update({
            'equipment': equipment,
        })
        return kwargs

    def get_success_url(self):
        return reverse('equipment.view', args=(self.object.id,))