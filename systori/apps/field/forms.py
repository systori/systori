from django import forms
from ..project.models import DailyPlan
from ..task.models import Task


class CompletionForm(forms.ModelForm):
    comment = forms.CharField(required=False)

    class Meta:
        model = Task
        fields = ['complete', 'comment']


class DailyPlanNoteForm(forms.ModelForm):
    class Meta:
        model = DailyPlan
        fields = ['notes']
