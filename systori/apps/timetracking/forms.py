import re

from datetime import timedelta

from django import forms
from django.forms import ModelForm, modelformset_factory, BaseModelFormSet, ValidationError
from django.core import validators

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


class DurationField(forms.Field):
    duration_re = re.compile(r'^(?P<sign>\-)?((?P<hours>\d+?)h)?\s?((?P<minutes>\d+?)m)?$')
    default_error_messages = {
        'invalid': _('Enter valid duration (example: 1h 10m)')
    }

    def to_python(self, value):
        if value in self.empty_values:
            return None
        match = self.duration_re.match(value)
        if not match:
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        bits = match.groupdict()
        sign = bits.pop('sign') or ''
        parsed_values = {k: int(sign + v) for k, v in bits.items() if v}
        return int(timedelta(**parsed_values).total_seconds())


class ManualTimerForm(ModelForm):

    class Meta:
        model = Timer
        fields = ['user', 'start', 'end', 'kind', 'comment']
        field_classes = {
            'user': UserChoiceField
        }

    # duration = DurationField(required=True, widget=forms.TextInput(
    #     attrs={'placeholder': '1h 30m', 'class': 'timetracking-form-duration'}))

    def __init__(self, company=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['start'].widget = DateTimeWidget(
            options={'format': 'dd.mm.yyyy hh:ii', 'pickerPosition': 'bottom-left'},
            attrs={'id':'timetracking-form-start'},
            bootstrap_version=3
        )
        self.fields['end'].widget = DateTimeWidget(
            options={'format': 'dd.mm.yyyy hh:ii', 'pickerPosition': 'bottom-left'},
            attrs={'id':'timetracking-form-end'},
            bootstrap_version=3
        )
        self.fields['start'].required = True
        self.fields['end'].required = True
        if company:
            self.fields['user'].queryset = company.active_users()

    def save(self, commit=True):
        data = self.cleaned_data
        span_days = (data['end'] - data['start']).days
        if commit and span_days > 1 and data['kind'] in self._meta.model.FULL_DAY_KINDS:
            return self._meta.model.objects.create_batch(days=span_days, **data)
        else:
            return super().save(commit)


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


class DayPickerForm(forms.Form):

    period = forms.DateField(widget=DateTimeWidget(
        options={
            'format': 'dd.mm.yyyy',
            'startView': 2,
            'pickerPosition': 'bottom-left',
            'minView': 2,
            'clearBtn': False
        },
        attrs={'id':'timetracking-report-period'},
        bootstrap_version=3
    ), input_formats=['%d.%m.%Y'])
