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
        fields = ['name', 'description', 'address', 'postal_code', 'city',

                  'level_1_zfill',

                  'has_level_2',
                  'level_2_zfill',
                  'level_2_name',

                  'has_level_3',
                  'level_3_zfill',
                  'level_3_name',

                  'has_level_4',
                  'level_4_zfill',
                  'level_4_name',

                  'has_level_5',
                  'level_5_zfill',
                  'level_5_name',

                  'task_zfill',

                  ]


class ProjectImportForm(forms.Form):
    file = forms.FileField(validators=[gaeb_validator])


class ProjectUpdateForm(ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description',

                  'level_1_zfill',

                  'has_level_2',
                  'level_2_zfill',
                  'level_2_name',

                  'has_level_3',
                  'level_3_zfill',
                  'level_3_name',

                  'has_level_4',
                  'level_4_zfill',
                  'level_4_name',

                  'has_level_5',
                  'level_5_zfill',
                  'level_5_name',

                  'task_zfill',

                  ]


class JobSiteForm(ModelForm):
    class Meta:
        model = JobSite
        fields = ['name', 'address', 'postal_code', 'city', 'travel_time']


class FilterForm(Form):
    OPTIONS = {
        ('contacts', _("Limit search to Contacts.")),
        ('jobs', _("Limit search to Jobs."))
    }

    search_option = forms.MultipleChoiceField(label=_('Limits'), widget=forms.CheckboxSelectMultiple,
                                              choices=OPTIONS, required=False)
    search_term = forms.CharField(label=_('Search'), max_length=50, required=False)

