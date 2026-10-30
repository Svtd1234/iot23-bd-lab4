from datetime import date, datetime


def to_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def to_datetime(value):
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    return datetime.fromisoformat(str(value).replace("T", " "))


def floor_hour(value):
    return to_datetime(value).replace(minute=0, second=0, microsecond=0)


def fmt_datetime(value):
    return to_datetime(value).strftime("%Y-%m-%d %H:%M:%S")
