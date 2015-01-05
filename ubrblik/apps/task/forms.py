from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    template_job = forms.ModelChoiceField(queryset=Job.objects.filter(project__is_template=True), required=False)
    class Meta:
        model = Job
        fields = ['name', 'description', 'billing_method', 'template_job']

class JobTemplateForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['name', 'description']