from django.forms import ModelForm
from django import forms
from .models import Project, JobSite
from django.utils.translation import ugettext_lazy as _


class ProjectCreateForm(ModelForm):
    address = forms.CharField(label=_("Address"), max_length=512)
    postal_code = forms.CharField(label=_("Postal Code"), max_length=512)
    city = forms.CharField(label=_("City"), max_length=512)

    class Meta:
        model = Project
        fields = ['name', 'description', 'job_zfill', 'taskgroup_zfill', 'task_zfill', 'job_offset',
                  'address', 'postal_code', 'city']


class ProjectImportForm(ModelForm):
    file = forms.FileField()
    
    class Meta:
        model = Project
        fields = ['file']


class ProjectUpdateForm(ModelForm):

    class Meta:
        model = Project
        fields = ['name', 'description', 'job_zfill', 'taskgroup_zfill', 'task_zfill', 'job_offset']


class JobSiteForm(ModelForm):

    class Meta:
        model = JobSite
        fields = ['name', 'address', 'postal_code', 'city']