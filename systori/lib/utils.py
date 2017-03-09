from collections import OrderedDict
from math import floor, ceil


class GenOrderedDict(OrderedDict):
    """

        OrderedDict with `.gen()` method which
        works similar to `.setdefault()`.

        Example usage:

        report = GenOrderedDict(
            lambda: GenOrderedDict(
                lambda: {
                    'timers': [],
                    'total': 0
                }
            )
        )

        for timer in self:
            date = timer.started.date()
            day_report = report.gen(date)
            worker_report = day_report.gen(timer.worker)
            worker_report['timers'].append(timer)
            if timer.kind != timer.UNPAID_LEAVE:
                worker_report['total'] += timer.running_duration
    """
    def __init__(self, generator):
        super().__init__()
        self.generator = generator

    def gen(self, key):
        return self.setdefault(key, self.generator())


def nice_percent(progress, total):
    percent = progress / total * 100 if total else 0
    if percent < 100:
        return ceil(percent)
    elif percent > 100:
        return floor(percent)
    else:
        return 100
