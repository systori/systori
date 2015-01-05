from django import forms
from .models import Job
from django.utils.translation import ugettext_lazy as _

class JobForm(forms.ModelForm):
    job_template = forms.ModelChoiceField(label=_('Job Template'), queryset=Job.objects.filter(project__is_template=True), required=False)
    class Meta:
        model = Job
        fields = ['name', 'description', 'billing_method', 'job_template']

class JobTemplateForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['name', 'description']