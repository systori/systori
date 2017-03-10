from datetime import date
from calendar import monthrange as _monthrange


def month_range(year, month):
    """ Returns tuple of two dates for the first
        and last day of a particular month.
        Useful in query filter, ex:
          .filter(document_date__range=date_utils.date_range(2016, 8))
        Produces:
          WHERE "document_date" BETWEEN 2016-08-01 AND 2016-08-31
    """
    start = date(year, month, 1)
    end = date(year, month, _monthrange(year, month)[1])
    return start, end


def last_day(year, month):
    return date(year, month, _monthrange(year, month)[1])
