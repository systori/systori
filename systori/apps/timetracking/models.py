import json
from datetime import timedelta

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from django.utils.translation import ugettext_lazy as _, ugettext as __
from django.core.exceptions import ValidationError

from ..project.models import JobSite
from .managers import TimerQuerySet


class Timer(models.Model):
    CORRECTION = 5
    WORK = 10
    EDUCATION = 15
    HOLIDAY = 20
    ILLNESS = 30

    KIND_CHOICES = (
        (WORK, _('Work')),
        (HOLIDAY, _('Holiday')),
        (ILLNESS, _('Illness')),
        (CORRECTION, _('Correction')),
        (EDUCATION, _('Education')),
    )
    FULL_DAY_KINDS = (WORK, HOLIDAY, ILLNESS)

    KIND_TO_STRING = {
        CORRECTION: 'correction',
        WORK: 'work',
        EDUCATION: 'education',
        HOLIDAY: 'holiday',
        ILLNESS: 'illness'
    }

    DAILY_BREAK = 60 * 60  # seconds
    WORK_HOURS = 60 * 60 * 8  # seconds
    WORK_DAY_START = (7, 00)
    SHORT_DURATION_THRESHOLD = 59

    duration_formulas = {
        WORK: lambda start, end: (end - start).total_seconds(),
        ILLNESS: lambda start, end: (end - start).total_seconds(),
        HOLIDAY: lambda start, end: (end - start).total_seconds(),
        CORRECTION: lambda start, end: (end - start).total_seconds(),
        EDUCATION: lambda start, end: (end - start).total_seconds()
    }

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateField(db_index=True)
    start = models.DateTimeField(blank=True, null=True, db_index=True)
    end = models.DateTimeField(blank=True, null=True, db_index=True)
    duration = models.IntegerField(default=0, help_text=_('in seconds'))
    kind = models.PositiveIntegerField(default=WORK, choices=KIND_CHOICES, db_index=True)
    altered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='timers_altered', blank=True, null=True)
    comment = models.CharField(max_length=1000, blank=True)
    start_latitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    start_longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    end_latitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    end_longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    job_site = models.ForeignKey(JobSite, blank=True, null=True)

    objects = TimerQuerySet.as_manager()

    class Meta:
        verbose_name = _('timer')
        verbose_name_plural = _('timers')
        ordering = ('start',)

    def __str__(self):
        return 'Timer for user#{}: start={}, end={}, duration={}, date={}'.format(
            self.user_id, self.start, self.end, self.duration, self.date
        )

    @classmethod
    def launch(cls, user, **kwargs):
        """
        Convenience method for consistency (so the class has not just stop but launch method as well)
        """
        timer = cls(user=user, **kwargs)
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
        return self.kind in (self.EDUCATION, self.HOLIDAY, self.ILLNESS)

    def _pre_save_for_generic(self):
        if not self.start:
            self.start = timezone.now()
        if self.end:
            self.duration = self.get_duration_seconds(self.end)
        elif self.duration:
            self.end = self.start + timedelta(seconds=self.duration)

    def clean(self):
        if self.pk:
            return
        user_timers = Timer.objects.filter(user=self.user)
        if not (self.end or self.duration) and user_timers.filter_running().exists():
            raise ValidationError(__('Timer already running'))
        if self.start:
            overlapping_timer = user_timers.filter(start__lte=self.start).filter(
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
        if self.duration > 60 * 60 * 24:
            raise ValidationError(__('Timer cannot be longer than 24 hours'))
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

    def stop(self, ignore_short_duration=True):
        assert self.pk
        self.end = timezone.now()
        if not ignore_short_duration or self.get_duration_seconds() > self.SHORT_DURATION_THRESHOLD:
            self.save()
        else:
            self.delete()

    def to_dict(self):
        return {'duration': self.get_duration()}
