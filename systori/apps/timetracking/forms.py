from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from datetimewidget.widgets import DateTimeWidget

from .models import Timer


class ManualTimerForm(ModelForm):

    morning_break = forms.BooleanField(label=_("Morning break"), initial=True, required=False)
    lunch_break = forms.BooleanField(label=_("Lunch break"), initial=True, required=False)

    class Meta:
        model = Timer
        fields = ['worker', 'started', 'stopped', 'kind', 'comment']

    def __init__(self, *args, company, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['started'].widget = DateTimeWidget(
            options={'format': 'dd.mm.yyyy hh:ii', 'pickerPosition': 'bottom-left'},
            attrs={'id': 'timetracking-form-started'},
            bootstrap_version=3
        )
        self.fields['stopped'].widget = DateTimeWidget(
            options={'format': 'dd.mm.yyyy hh:ii', 'pickerPosition': 'bottom-left'},
            attrs={'id':'timetracking-form-stopped'},
            bootstrap_version=3
        )
        self.fields['started'].required = True
        self.fields['stopped'].required = True
        self.fields['worker'].queryset = company.active_workers(is_timetracking_enabled=True)

    def clean(self):
        if self.cleaned_data['kind'] != self._meta.model.WORK and \
           any([self.cleaned_data['morning_break'], self.cleaned_data['lunch_break']]):
            self.add_error(None, _('Only work timers can have morning or lunch breaks.'))

    def save(self, commit=True):
        return self._meta.model.objects.create_batch(commit=commit, **self.cleaned_data)


class WorkerManualTimerForm(ManualTimerForm):

    class Meta(ManualTimerForm.Meta):
        widgets = {
            'worker': forms.HiddenInput()
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
        attrs={'id': 'timetracking-report-period'},
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
        attrs={'id': 'timetracking-report-period'},
        bootstrap_version=3
    ), input_formats=['%d.%m.%Y'])
