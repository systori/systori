from datetime import timedelta

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from django.utils.translation import ugettext_lazy as _, ugettext as __
from django.core.exceptions import ValidationError

from ..project.models import JobSite
from .managers import TimerQuerySet
from .utils import round_to_nearest_multiple


class Timer(models.Model):
    CORRECTION = 'correction'
    WORK = 'work'
    TRAINING = 'training'
    HOLIDAY = 'holiday'
    ILLNESS = 'illness'
    # PUBLIC_HOLIDAY = 'public_holiday'
    # UNPAID_LEAVE = 'unpaid_leave'
    #TODO: public_holiday (8hrs work time) and unpaid_leave (0hrs work time) types

    KIND_CHOICES = (
        (WORK, _('Work')),
        (HOLIDAY, _('Holiday')),
        (ILLNESS, _('Illness')),
        (CORRECTION, _('Correction')),
        (TRAINING, _('Training')),
        # (PUBLIC_HOLIDAY, _('Public holiday')),
        # (UNPAID_LEAVE, _('Unpaid leave')),
    )
    FULL_DAY_KINDS = (WORK, HOLIDAY, ILLNESS)

    DAILY_BREAK = 60 * 60  # seconds
    WORK_HOURS = 60 * 60 * 8  # seconds
    WORK_DAY_START = (7, 00)
    SHORT_DURATION_THRESHOLD = 59

    duration_formulas = {
        WORK: lambda start, end: (end - start).total_seconds(),
        ILLNESS: lambda start, end: (end - start).total_seconds(),
        HOLIDAY: lambda start, end: (end - start).total_seconds(),
        CORRECTION: lambda start, end: (end - start).total_seconds(),
        TRAINING: lambda start, end: (end - start).total_seconds(),
        # PUBLIC_HOLIDAY: lambda start, end: (end - start).total_seconds(),
        # UNPAID_LEAVE: lambda start, end: (end - start).total_seconds(),
    }

    worker = models.ForeignKey('company.Worker', related_name='timers')
    date = models.DateField(db_index=True)
    start = models.DateTimeField(blank=True, null=True, db_index=True)
    end = models.DateTimeField(blank=True, null=True, db_index=True)
    duration = models.IntegerField(default=0, help_text=_('in seconds'))
    kind = models.CharField(default=WORK, choices=KIND_CHOICES, db_index=True, max_length=32)
    comment = models.CharField(max_length=1000, blank=True)
    start_latitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    start_longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    end_latitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    end_longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    job_site = models.ForeignKey(JobSite, blank=True, null=True)
    is_auto_started = models.BooleanField(default=False)
    is_auto_stopped = models.BooleanField(default=False)

    objects = TimerQuerySet.as_manager()

    class Meta:
        verbose_name = _('timer')
        verbose_name_plural = _('timers')
        ordering = ('start',)

    def __str__(self):
        return 'Timer #{}: date={:%Y-%m-%d}, start={:%H:%M}, end={:%H:%M}, duration={}'.format(
            self.id, self.date, self.start, self.end, self.get_duration_formatted()
        )

    @classmethod
    def launch(cls, worker, **kwargs):
        """
        Convenience method for consistency (so the class has not just stop but launch method as well)
        """
        timer = cls(worker=worker, **kwargs)
        timer.clean()
        timer.save()
        return timer

    @property
    def is_running(self):
        return not self.end

    @property
    def is_working(self):
        return self.kind == self.WORK

    @property
    def is_busy(self):
        return self.kind in (self.TRAINING, self.HOLIDAY, self.ILLNESS)

    def _pre_save_for_generic(self):
        if not self.start:
            self.start = timezone.now()
        if self.end:
            self.duration = round_to_nearest_multiple(self.get_duration_seconds(self.end))
        elif self.duration:
            self.end = self.start + timedelta(seconds=self.duration)

    def clean(self):
        if self.pk:
            return
        worker_timers = Timer.objects.filter(worker=self.worker)
        if not (self.end or self.duration) and worker_timers.filter_running().exists():
            raise ValidationError(__('Timer already running'))
        if self.start:
            overlapping_timer = worker_timers.filter(start__lte=self.start).filter(
                Q(end__gte=self.start) | Q(end__isnull=True)
            ).first()
            if overlapping_timer:
                if overlapping_timer.end:
                    message = __(
                        'Overlapping timer ({:%d.%m.%Y %H:%M}—{:%d.%m.%Y %H:%M}) already exists'
                    ).format(overlapping_timer.start, overlapping_timer.end)
                else:
                    message = __(
                        'A potentially overlapping timer (started on {:%d.%m.%Y %H:%M}) is already running'
                    ).format(overlapping_timer.start)
                raise ValidationError(message)
        if self.start and self.end and self.start > self.end:
            raise ValidationError(__('Timer cannot be negative'))

    def save(self, *args, **kwargs):
        self._pre_save_for_generic()

        if not self.date:
            self.date = self.start.date() if self.start else timezone.now().date()
        super().save(*args, **kwargs)

    def get_duration_seconds(self, now=None):
        if self.duration:
            return self.duration
        if not now:
            now = timezone.now()
        return int(self.duration_formulas[self.kind](self.start, now))

    def get_duration(self, now=None):
        seconds = self.get_duration_seconds(now)
        return [int(v) for v in (seconds // 3600, (seconds % 3600) // 60, seconds % 60)]

    def get_duration_formatted(self):
        from .utils import format_seconds
        return format_seconds(self.get_duration_seconds())

    def stop(self, end=None, ignore_short_duration=True, **kwargs):
        assert self.pk
        self.end = end or timezone.now()
        for field, value in kwargs.items():
            setattr(self, field, value)
        if not ignore_short_duration or self.get_duration_seconds() > self.SHORT_DURATION_THRESHOLD:
            self.save()
        else:
            self.delete()

    def to_dict(self):
        return {'duration': self.get_duration()}
