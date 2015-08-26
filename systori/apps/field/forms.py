from django import forms
from systori.lib.fields import LocalizedDecimalField
from ..project.models import DailyPlan
from ..task.models import Task


class CompletionForm(forms.ModelForm):
    comment = forms.CharField(required=False)
    complete = LocalizedDecimalField(max_digits=14, decimal_places=4)

    class Meta:
        model = Task
        fields = ['complete', 'comment']


class DailyPlanNoteForm(forms.ModelForm):
    class Meta:
        model = DailyPlan
        fields = ['notes']
