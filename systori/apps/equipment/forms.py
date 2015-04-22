from django.forms import ModelForm
from .models import Equipment


class EquipmentForm(ModelForm):
    class Meta:
        model = Equipment
        exclude = []