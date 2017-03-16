from django import forms
from ..project.models import DailyPlan
from ..task.models import Task


class CompletionForm(forms.ModelForm):
    comment = forms.CharField(required=False)
    complete = forms.DecimalField(localize=True, max_digits=14, decimal_places=4)

    class Meta:
        model = Task
        fields = ['complete', 'comment', 'status']


class DailyPlanNoteForm(forms.ModelForm):
    class Meta:
        model = DailyPlan
        fields = ['notes']
