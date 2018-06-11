from django.utils.translation import ugettext_lazy as _

WEEKDAYS = [_("Mon"), _("Tue"), _("Wed"), _("Thu"), _("Fri"), _("Sat"), _("Sun")]


def get_weekday_names_numbers_and_mondays(start, days, pad=True):
    names = []
    numbers = []
    mondays = []
    for day in range(31) if pad else range(days):
        if day < days:
            names.append(WEEKDAYS[(day + start) % 7])
            if ((day + start) % 7) == 0:
                mondays.append(day)
            numbers.append(str(day + 1))
        else:
            names.append("")
            numbers.append("")
    return names, numbers, mondays
