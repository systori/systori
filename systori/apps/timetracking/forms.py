import re

from datetime import timedelta

from django import forms
from django.forms import ModelForm, modelformset_factory, BaseModelFormSet, ValidationError
from django.utils.translation import ugettext as __
from django.core import validators

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from datetimewidget.widgets import DateTimeWidget

from .models import Timer


class WorkerForm(ModelForm):

    class Meta:
        model = Timer
        fields = ['kind']

    def __init__(self, worker, *args, **kwargs):
        self.worker = worker
        super().__init__(*args, **kwargs)

    def clean(self):
        if Timer.objects.filter(worker=self.worker, end__isnull=True).exists():
            raise forms.ValidationError(_('Timer already running'))

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        instance.worker = self.worker


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

    include_weekends = forms.BooleanField(label=_("Include weekends"), initial=False, required=False)
    morning_break = forms.BooleanField(label=_("Morning break"), initial=True, required=False)
    lunch_break = forms.BooleanField(label=_("Lunch break"), initial=True, required=False)

    class Meta:
        model = Timer
        fields = ['worker', 'start', 'end', 'kind', 'comment']

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
            self.fields['worker'].queryset = company.active_workers(is_timetracking_enabled=True)

    def clean(self):
        data = self.cleaned_data
        if data['start'] and data['end'] and data['start'] > data['end']:
            raise ValidationError({'start': __('Timer cannot be negative')})
        return data

    def save(self, commit=True):
        return self._meta.model.objects.create_batch(commit=commit, **self.cleaned_data)


class WorkerManualTimerForm(ManualTimerForm):

    class Meta(ManualTimerForm.Meta):
        widgets = {
            'worker': forms.HiddenInput()
        }


class MultipleWorkerManualTimerForm(ManualTimerForm):

    class Meta(ManualTimerForm.Meta):
        exclude = ['worker']

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
            self.fields['worker'].queryset = company.active_workers()

    def clean(self):
        data = self.cleaned_data
        if data['start'] and data['end'] and data['start'] > data['end']:
            raise ValidationError({'start': __('Timer cannot be negative')})
        return data

    def save(self, commit=True):
        return self._meta.model.objects.create_batch(commit=commit, **self.cleaned_data)


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
