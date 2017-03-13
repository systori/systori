import re

from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from datetimewidget.widgets import DateTimeWidget as OldDateTimeWidget

from .models import Timer


class DateTimeWidget(OldDateTimeWidget):

    EXTRACT_INIT_JS = re.compile('(.*?)<script.*?>(.*?)</script>', re.DOTALL)

    def __init__(self, name, options, required=False):
        super().__init__(options=options, attrs={'id': 'timetracking-'+name}, bootstrap_version=3)
        self.required = required
        self.init_javascript = ''

    def render(self, name, value, attrs=None, renderer=None):
        rendered_widget = super().render(name, value, attrs)
        html, self.init_javascript = self.EXTRACT_INIT_JS.search(rendered_widget).groups()
        return html


class ManualTimerForm(ModelForm):

    morning_break = forms.BooleanField(label=_("Morning break"), initial=True, required=False)
    lunch_break = forms.BooleanField(label=_("Lunch break"), initial=True, required=False)

    class Meta:
        model = Timer
        fields = ['worker', 'started', 'stopped', 'kind', 'comment']

    def __init__(self, *args, company, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['started'].widget = DateTimeWidget(
            'form-started', {'format': 'dd.mm.yyyy hh:ii', 'pickerPosition': 'bottom-left'}, True
        )
        self.fields['stopped'].widget = DateTimeWidget(
            'form-stopped', {'format': 'dd.mm.yyyy hh:ii', 'pickerPosition': 'bottom-left'}, True
        )
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
        'report-period',
        options={
            'format': 'mm.yyyy',
            'startView': 3,
            'pickerPosition': 'bottom-left',
            'minView': 3,
            'clearBtn': False
        },
    ), input_formats=['%m.%Y'])


class DayPickerForm(forms.Form):

    period = forms.DateField(widget=DateTimeWidget(
        'report-period',
        options={
            'format': 'dd.mm.yyyy',
            'startView': 2,
            'pickerPosition': 'bottom-left',
            'minView': 2,
            'clearBtn': False
        },
    ), input_formats=['%d.%m.%Y'])
