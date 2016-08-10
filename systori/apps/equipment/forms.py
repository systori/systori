from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Equipment, RefuelingStop


class EquipmentForm(forms.ModelForm):
    last_refueling_stop = forms.DateField(_('last_refueling_stop'), disabled=True)

    class Meta:
        model = Equipment
        exclude = []


class RefuelingStopForm(forms.ModelForm):
    class Meta:
        model = RefuelingStop
        exclude = []