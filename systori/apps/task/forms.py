from django import forms
from .models import Job
from django.utils.translation import ugettext_lazy as _
from ..accounting.models import create_account_for_job


class JobTemplateCreateForm(forms.ModelForm):

    class Meta:
        model = Job
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True

    def save(self, commit=True):
        job = super().save(commit)
        job.job = job
        job.account = create_account_for_job(job)
        job.generate_groups()
        job.save()
        return job


class JobCreateForm(forms.ModelForm):

    job_template = forms.ModelChoiceField(
        label=_('Job Template'),
        queryset=Job.objects.filter(project__is_template=True),
        required=False
    )

    class Meta:
        model = Job
        fields = ['name', 'description', 'billing_method', 'job_template']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True

    def save(self, commit=True):
        job = super().save(commit)
        job.job = job
        job.account = create_account_for_job(job)
        if self.cleaned_data['job_template']:
            tmpl = self.cleaned_data['job_template']
            tmpl.clone_to(job)
        else:
            job.generate_groups()
        job.save()
        return job
