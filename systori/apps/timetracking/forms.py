from datetime import datetime
from django import forms
from django.forms import ModelForm
from django.utils.timezone import make_aware
from django.utils.formats import get_format_lazy
from django.utils.translation import ugettext_lazy as _
from bootstrap import DateField, DateWidget, TimeField, DateRangeField, DateRangeWidget

from .models import Timer


class ManualTimerForm(ModelForm):

    dates = DateRangeField(
        require_end=False, widget=DateRangeWidget(options={"separator": _(" to ")})
    )
    start = TimeField()
    stop = TimeField()
    morning_break = forms.BooleanField(
        label=_("Morning break"), initial=True, required=False
    )
    lunch_break = forms.BooleanField(
        label=_("Lunch break"), initial=True, required=False
    )
    workers = forms.ModelMultipleChoiceField(queryset=None)

    class Meta:
        model = Timer
        fields = [
            "dates",
            "start",
            "stop",
            "kind",
            "morning_break",
            "lunch_break",
            "comment",
        ]

    def __init__(self, *args, company, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["workers"].queryset = company.tracked_workers().order_by(
            "user__last_name"
        )

    def _post_clean(self):
        for worker in self.cleaned_data["workers"]:
            self.instance.worker = worker
            super()._post_clean()

    def clean(self):
        if self.cleaned_data["kind"] != Timer.WORK and any(
            [self.cleaned_data["morning_break"], self.cleaned_data["lunch_break"]]
        ):
            self.add_error(
                None, _("Only work timers can have morning or lunch breaks.")
            )
        start_date, stop_date = self.cleaned_data["dates"]
        start_time = self.cleaned_data["start"]
        stop_time = self.cleaned_data["stop"]
        # self.instance here is never actually saved, Django uses
        # it as part of the validation by calling Timer.clean()
        if start_date and start_time and stop_time:
            self.instance.started = make_aware(datetime.combine(start_date, start_time))
            if not stop_date:
                stop_date = start_date
            self.instance.stopped = make_aware(datetime.combine(stop_date, stop_time))

    def save(self, commit=True):
        timers = []
        for worker in self.cleaned_data.pop("workers"):
            timers.extend(
                Timer.objects.create_batch(
                    commit=commit, worker=worker, **self.cleaned_data
                )
            )
        return timers


class WorkerManualTimerForm(ManualTimerForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields["workers"]

    def _post_clean(self):
        self.cleaned_data["workers"] = self.initial["workers"]
        super()._post_clean()


class MonthPickerForm(forms.Form):
    MONTH_INPUT = get_format_lazy("YEAR_MONTH_INPUT_FORMATS")
    period = DateField(
        input_formats=MONTH_INPUT,
        widget=DateWidget(
            input_formats=MONTH_INPUT,
            options={"minViewMode": "months", "maxViewMode": "years"},
        ),
    )


class DayPickerForm(forms.Form):
    period = DateField()
