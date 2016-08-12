from django import forms
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Equipment, RefuelingStop, Defect


class EquipmentForm(forms.ModelForm):
    last_refueling_stop = forms.DateField(_('last_refueling_stop'), disabled=True, required=False)

    class Meta:
        model = Equipment
        exclude = []


class RefuelingStopForm(forms.ModelForm):
    distance = forms.DecimalField(_('distance'), disabled=True, required=False)
    average_consumption = forms.DecimalField(_('average_consumption'), disabled=True, required=False)

    class Meta:
        model = RefuelingStop
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove broken MaxValueValidator that django imposes
        # on DecimalField with disabled=True for some reason
        self.fields['distance'].validators.pop(0)
        self.fields['average_consumption'].validators.pop(0)

    def clean_mileage(self):
        mileage = self.cleaned_data.get('mileage')
        older_refueling_stop = RefuelingStop.objects.filter(equipment=self.cleaned_data.get('equipment').id,
                                                            mileage__gt=mileage).order_by('mileage').first()
        # todo: check if self.instance.older_refueling_stop could be replaced with local older_refueling_stop
        if self.instance.pk:
            if self.instance.older_refueling_stop is not None and mileage <= self.instance.older_refueling_stop.mileage:
                    raise ValidationError(_('you must enter a higher mileage than the older refueling stop.'))
            elif self.instance.younger_refueling_stop and mileage >= self.instance.younger_refueling_stop.mileage:
                raise ValidationError(_('you must enter a smaller mileage than the younger refueling stop.'))
            return mileage
        elif older_refueling_stop and mileage <= older_refueling_stop.mileage:
            raise ValidationError(_('you must enter a higher mileage than the older refueling stop.'))

        return mileage


class DefectForm(forms.ModelForm):
    class Meta:
        model = Defect
        exclude = []
