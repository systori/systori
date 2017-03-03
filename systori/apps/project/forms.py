from django.forms import ModelForm
from django import forms
from .models import Project, JobSite


class ProjectCreateForm(ModelForm):

    class Meta:
        model = Project
        fields = ['name', 'description', 'structure']


class ProjectUpdateForm(ModelForm):

    class Meta:
        model = Project
        fields = ['name', 'description', 'structure']

    def clean_structure(self):
        structure = self.cleaned_data.get("structure")
        if self.instance.structure_depth != structure.maximum_depth:
            raise forms.ValidationError(
                "Cannot change depth after project has been created.",
                code='invalid',
            )
        return structure


class JobSiteForm(ModelForm):
    class Meta:
        model = JobSite
        fields = ['name', 'address', 'postal_code', 'city', 'travel_time']

    def save(self, commit=True):
        self.instance.geocode_address()
        return super().save(commit)


class GAEBImportForm(forms.Form):
    file = forms.FileField()