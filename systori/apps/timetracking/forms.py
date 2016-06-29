import re

from datetime import timedelta

from django import forms
from django.forms import ModelForm, modelformset_factory, BaseModelFormSet
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from datetimewidget.widgets import DateTimeWidget

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

    def __init__(self, company, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['start'].widget = DateTimeWidget(
            options={'format': 'dd.mm.yyyy HH:ii', 'pickerPosition': 'bottom-left'},
            attrs={'id':'timetracking-form-start'},
            bootstrap_version=3,
            # usel10n=True
        )
        self.fields['user'].queryset = company.active_users()

    def clean_duration(self):
        raw_value = self.cleaned_data['duration']
        parsed_values = {k: int(v) for k, v in DURATION_RE.match(raw_value).groupdict().items() if v}
        return int(timedelta(**parsed_values).total_seconds())


class UserManualTimerForm(ManualTimerForm):

    class Meta(ManualTimerForm.Meta):
        widgets = {
            'user': forms.HiddenInput()
        }


class MonthPickerForm(forms.Form):

    period = forms.DateField(widget=DateTimeWidget(
        options={
            'format': 'mm.yyyy',
            'startView': 3,
            'pickerPosition': 'bottom-left',
            'minView': 3,
            'clearBtn': False
        },
        attrs={'id':'timetracking-report-period'},
        bootstrap_version=3
    ), input_formats=['%m.%Y'])
