from django import forms
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Equipment, RefuelingStop, Defect


class EquipmentForm(forms.ModelForm):
    last_refueling_stop = forms.DateField(_('last_refueling_stop'), disabled=True)

    class Meta:
        model = Equipment
        exclude = []


class RefuelingStopForm(forms.ModelForm):
    class Meta:
        model = RefuelingStop
        exclude = []

    #def clean(self):
    #    cleaned_data = super(RefuelingStopForm, self).clean()
    #    mileage = cleaned_data.get('mileage')
    #    if self.instance.pk:
    #        if mileage <= self.instance.older_refueling_stop.mileage:
    #            self.add_error('mileage', _('you must enter a higher mileage than the older refueling stop.'))
    #        elif mileage >= self.instance.younger_refueling_stop.mileage:
    #            self.add_error('mileage', _('you must enter a smaller mileage than the younger refueling stop.'))

    def clean_mileage(self):
        mileage = self.cleaned_data.get('mileage')
        if self.instance.pk:
            if self.instance.older_refueling_stop and mileage <= self.instance.older_refueling_stop.mileage:
                raise ValidationError(_('you must enter a higher mileage than the older refueling stop.'))
            elif self.instance.younger_refueling_stop and mileage >= self.instance.younger_refueling_stop.mileage:
                raise ValidationError(_('you must enter a smaller mileage than the younger refueling stop.'))
            return mileage
        return mileage


class DefectForm(forms.ModelForm):
    class Meta:
        model = Defect
        exclude = []