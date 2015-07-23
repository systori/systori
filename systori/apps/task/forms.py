from django import forms
from .models import Job
from django.utils.translation import ugettext_lazy as _


class JobForm(forms.ModelForm):
    job_template = forms.ModelChoiceField(label=_('Job Template'),
                                          queryset=Job.objects.filter(project__is_template=True), required=False)

    class Meta:
        model = Job
        fields = ['job_code', 'name', 'description', 'billing_method', 'job_template', 'taskgroup_offset']


class JobTemplateForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['name', 'description', 'taskgroup_offset']
