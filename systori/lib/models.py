from django.utils.translation import ugettext_lazy as _


def apply_all_kwargs(obj, **kwargs):
    for field in obj._meta.get_fields():
        if field.attname in kwargs:
            value = kwargs.pop(field.attname)
            setattr(obj, field.attname, value)
    if kwargs:
        raise TypeError(
            "'{}' is not a valid field of {}"
            .format(list(kwargs)[0], obj.__class__.__name__)
        )


class RateType:
    HOURLY = 'hourly'
    DAILY = 'daily'
    WEEKLY = 'weekly'
    FLAT = 'flat'
    RATE_CHOICES = [
        (HOURLY, _("Hourly")),
        (DAILY, _("Daily")),
        (WEEKLY, _("Weekly")),
        (FLAT, _("Flat Fee")),
    ]
