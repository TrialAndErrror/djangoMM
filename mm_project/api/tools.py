import datetime
from dateutil.relativedelta import relativedelta

a_month = relativedelta(months=1)
calc_date = {
    'day': datetime.timedelta(days=1),
    'week': datetime.timedelta(weeks=1),
    'biweek': datetime.timedelta(weeks=2),
    'month': a_month,
    'quarter': a_month * 3,
    'biyear': a_month * 6,
    'year': a_month * 12
}


def get_next_date(date, period):
    return date + calc_date[period]
