from django.forms import ModelForm, Form
from django import forms
from .models import Project, JobSite
from .gaeb_utils import gaeb_validator
from django.utils.translation import ugettext_lazy as _

from ..task.models import Job
from ..task.forms import JobCreateForm


class ProjectCreateForm(ModelForm):
    address = forms.CharField(label=_('Address'), max_length=512)
    postal_code = forms.CharField(label=_('Postal Code'), max_length=512)
    city = forms.CharField(label=_('City'), max_length=512)

    class Meta:
        model = Project
        fields = ['name', 'description', 'address', 'postal_code', 'city', 'structure_format']

    def save(self, commit=True):

        project = super().save(commit)

        JobCreateForm(data={
            'name': project.name,
            'billing_method': Job.FIXED_PRICE,
        }, instance=Job(project=project)).save(commit)

        JobSiteForm(data={
            'name': _('Main Site'),
            'address': self.cleaned_data['address'],
            'city': self.cleaned_data['city'],
            'postal_code': self.cleaned_data['postal_code'],
            'project': project,
        }, instance=JobSite(project=project)).save(commit)

        return project


class ProjectImportForm(forms.Form):
    file = forms.FileField(validators=[gaeb_validator])


class ProjectUpdateForm(ModelForm):
    # TODO: User should only be able to change the formatting of the
    #       structure_format but not the number of levels. Need validation.
    class Meta:
        model = Project
        fields = ['name', 'description', 'structure_format']


class JobSiteForm(ModelForm):
    class Meta:
        model = JobSite
        fields = ['name', 'address', 'postal_code', 'city', 'travel_time']

    def save(self, commit=True):
        self.instance.geocode_address()
        return super().save(commit)
