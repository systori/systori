from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from ..project.models import JobSite
from .managers import TimerQuerySet
from .utils import (
    calculate_duration_minutes,
    calculate_duration_seconds,
    to_current_timezone,
)
from systori.lib.fields import apply_all_kwargs


class Timer(models.Model):

    # Work produces paid hours up to 8hrs daily.
    # After 8hrs it produces overtime hours.
    WORK = "work"

    # Vacation accumulates at some rate during period of employment.
    # Using vacation subtracts from accumulated vacation balance.
    # Replaces up to 8hrs of WORK.
    VACATION = "vacation"

    # Replaces up to 8hrs of WORK with doctors note.
    SICK = "sick"

    # Replaces up to 8hrs of WORK per local holiday laws.
    PUBLIC_HOLIDAY = "public_holiday"

    # Draws from overtime hours and replaces up to 8hrs of WORK.
    PAID_LEAVE = "paid_leave"

    # Fills up to 8hrs of WORK as unpaid time.
    UNPAID_LEAVE = "unpaid_leave"

    # Unsaved kind, used for reports to show breaks between work timers.
    BREAK = "break"

    KIND_CHOICES = (
        (WORK, _("Work")),
        (VACATION, _("Vacation")),
        (SICK, _("Sick")),
        (PUBLIC_HOLIDAY, _("Public holiday")),
        (PAID_LEAVE, _("Paid leave")),
        (UNPAID_LEAVE, _("Unpaid leave")),
    )

    DAILY_BREAK = 60
    WORK_HOURS = 60 * 8
    WORK_DAY_START = (7, 00)

    worker = models.ForeignKey(
        "company.Worker", related_name="timers", on_delete=models.CASCADE
    )
    started = models.DateTimeField(db_index=True)
    stopped = models.DateTimeField(blank=True, null=True, db_index=True)
    duration = models.IntegerField(default=0, help_text=_("in minutes"))
    kind = models.CharField(
        default=WORK, choices=KIND_CHOICES, db_index=True, max_length=32
    )
    comment = models.CharField(max_length=1000, blank=True)
    starting_latitude = models.DecimalField(
        max_digits=11, decimal_places=8, blank=True, null=True
    )
    starting_longitude = models.DecimalField(
        max_digits=11, decimal_places=8, blank=True, null=True
    )
    ending_latitude = models.DecimalField(
        max_digits=11, decimal_places=8, blank=True, null=True
    )
    ending_longitude = models.DecimalField(
        max_digits=11, decimal_places=8, blank=True, null=True
    )
    job_site = models.ForeignKey(
        JobSite, blank=True, null=True, on_delete=models.SET_NULL
    )
    is_auto_started = models.BooleanField(default=False)
    is_auto_stopped = models.BooleanField(default=False)

    objects = TimerQuerySet.as_manager()

    class Meta:
        verbose_name = _("timer")
        verbose_name_plural = _("timers")
        ordering = ("started",)

    def __str__(self):
        return "Timer #{}: date={:%Y-%m-%d}, started={:%H:%M}, stopped={}, duration={}".format(
            self.id,
            self.started,
            self.started,
            "{:%H:%M}".format(self.stopped) if self.stopped else "--:--",
            self.running_duration,
        )

    @classmethod
    def start(cls, worker, started=None, **kwargs):
        timer = cls(worker=worker, started=started or timezone.now(), **kwargs)
        timer.clean()
        timer.save()
        return timer

    def stop(self, stopped=None, **kwargs):
        assert self.stopped is None
        self.stopped = stopped or timezone.now()
        apply_all_kwargs(self, **kwargs)
        if self.running_duration > 0:
            self.save()
        else:
            self.delete()

    @property
    def is_working(self):
        return self.kind == self.WORK

    @property
    def is_running(self):
        return not self.stopped

    @property
    def running_duration(self):
        return calculate_duration_minutes(self.started, self.stopped)

    @property
    def running_duration_seconds(self):
        return calculate_duration_seconds(self.started, self.stopped)

    def clean(self):
        if self.started and self.stopped and self.started > self.stopped:
            raise ValidationError(_("Timer cannot be negative"))
        if self.pk:
            return
        worker_timers = Timer.objects.filter(worker=self.worker)
        if not (self.stopped or self.duration) and worker_timers.running().exists():
            raise ValidationError(_("Timer already running"))
        if self.started:
            overlapping_timer = (
                worker_timers.filter(started__lte=self.started)
                .filter(Q(stopped__gte=self.started) | Q(stopped__isnull=True))
                .first()
            )
            if overlapping_timer:
                if overlapping_timer.stopped:
                    message = _(
                        "Overlapping timer ({:%d.%m.%Y %H:%M} — {:%d.%m.%Y %H:%M}) already exists"
                    ).format(
                        to_current_timezone(overlapping_timer.started),
                        to_current_timezone(overlapping_timer.stopped),
                    )
                else:
                    message = _(
                        "A potentially overlapping timer (started on {:%d.%m.%Y %H:%M}) is already running"
                    ).format(overlapping_timer.started)
                raise ValidationError(message)

    def save(self, *args, **kwargs):
        if self.stopped and not self.duration:
            self.duration = self.running_duration
        super().save(*args, **kwargs)
