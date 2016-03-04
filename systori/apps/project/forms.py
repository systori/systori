from django.forms import ModelForm, Form
from django.forms.models import inlineformset_factory
from django import forms
from ..accounting.models import Transaction, Entry
from .models import Project, JobSite
from .gaeb_utils import gaeb_validator
from django.utils.translation import ugettext_lazy as _


class ProjectCreateForm(ModelForm):
    address = forms.CharField(label=_('Address'), max_length=512)
    postal_code = forms.CharField(label=_('Postal Code'), max_length=512)
    city = forms.CharField(label=_('City'), max_length=512)

    class Meta:
        model = Project
        fields = ['name', 'description', 'job_zfill', 'taskgroup_zfill', 'task_zfill',
                  'address', 'postal_code', 'city']


class ProjectImportForm(forms.Form):
    file = forms.FileField(validators=[gaeb_validator])


class ProjectUpdateForm(ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'job_zfill', 'taskgroup_zfill', 'task_zfill']


class JobSiteForm(ModelForm):
    class Meta:
        model = JobSite
        fields = ['name', 'address', 'postal_code', 'city']


class FilterForm(Form):
    OPTIONS = {
        ('contacts', _("Limit search to Contacts.")),
        ('jobs', _("Limit search to Jobs."))
    }

    search_option = forms.MultipleChoiceField(label=_('Limits'), widget=forms.CheckboxSelectMultiple,
                                              choices=OPTIONS, required=False)
    search_term = forms.CharField(label=_('Search'), max_length=50, required=False)

