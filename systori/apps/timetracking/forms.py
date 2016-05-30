import re

from datetime import timedelta

from django import forms
from django.forms import ModelForm, modelformset_factory, BaseModelFormSet
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .models import Timer


class UserForm(ModelForm):

    class Meta:
        model = Timer
        fields = ['kind']

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        if Timer.objects.filter(user=self.user, end__isnull=True).exists():
            raise forms.ValidationError(_('Timer already running'))

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        instance.user = self.user


class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name()


DURATION_RE = re.compile(r'((?P<hours>\d+?)h)?\s?((?P<minutes>\d+?)m)?')


class ManualTimerForm(ModelForm):

    class Meta:
        model = Timer
        fields = ['user', 'start', 'duration', 'kind']
        field_classes = {
            'user': UserChoiceField
        }

    duration = forms.RegexField(regex=DURATION_RE, required=True, widget=forms.TextInput(
        attrs={'placeholder': '1h 30m', 'class': 'timetracking-form-duration'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['user'].widget = forms.HiddenInput()

        # self.fields['start'].widget = forms.DateTimeInput(
        #     format='%Y-%m-%dT%H:%M',
        #     attrs={'type': 'datetime-local', 'class': 'timetracking-form-start'})
        from datetimewidget.widgets import DateTimeWidget

        self.fields['start'].widget = DateTimeWidget(attrs={
            'id':'timetracking-form-start'}, usel10n=True, bootstrap_version=3)

    def clean_duration(self):
        raw_value = self.cleaned_data['duration']
        parsed_values = {k: int(v) for k, v in DURATION_RE.match(raw_value).groupdict().items() if v}
        return int(timedelta(**parsed_values).total_seconds())


class UserManualTimerForm(ManualTimerForm):

    class Meta(ManualTimerForm.Meta):
        widgets = {
            'user': forms.HiddenInput()
        }
