from django.forms import ModelForm
from ..task.models import Task


class CompletionForm(ModelForm):
    class Meta:
        model = Task
        fields = ['complete']