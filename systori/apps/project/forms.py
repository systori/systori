from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from systori.apps.task.gaeb.convert import Import
from .models import Project, JobSite


class ProjectCreateForm(ModelForm):

    class Meta:
        model = Project
        fields = ['name', 'description', 'structure']


class ProjectUpdateForm(ProjectCreateForm):

    def clean_structure(self):
        structure = self.cleaned_data.get("structure")
        if self.instance.structure_depth != structure.maximum_depth:
            raise forms.ValidationError(
                "Cannot change depth after project has been created.",
                code='invalid',
            )
        return structure


class ProjectImportForm(ModelForm):
    file = forms.FileField(label=_('GAEB File'))

    class Meta:
        model = Project
        fields = ['file', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.importer = Import(self.instance, self)

    def clean(self):
        super().clean()
        self.importer.parse(self.files['file'])

    def save(self, commit=True):
        project = super().save(commit)
        self.importer.save()
        return project


class JobSiteForm(ModelForm):
    class Meta:
        model = JobSite
        fields = ['name', 'address', 'postal_code', 'city', 'travel_time']

    def save(self, commit=True):
        self.instance.geocode_address()
        return super().save(commit)
