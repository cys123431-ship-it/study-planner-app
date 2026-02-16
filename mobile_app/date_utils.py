import datetime


def current_date():
    return datetime.date.today()


def to_date_str(value=None):
    target = value or current_date()
    return target.strftime("%Y-%m-%d")


def to_month_str(value=None):
    target = value or current_date()
    return target.strftime("%Y-%m")


def to_iso_week_str(value=None):
    target = value or current_date()
    iso_year, iso_week, _ = target.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"
