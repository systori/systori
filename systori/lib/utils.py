from math import floor, ceil


def nice_percent(progress, total):
    percent = progress / total * 100 if total else 0
    if percent < 100:
        return ceil(percent)
    elif percent > 100:
        return floor(percent)
    else:
        return 100
