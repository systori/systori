from django import forms
from ..task.models import Task


class CompletionForm(forms.ModelForm):
    comment = forms.CharField(required=False)
    class Meta:
        model = Task
        fields = ['complete', 'comment']