from datetime import datetime

DAYS = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]

def letters_day(date):
    "%Y-%m-%dT%H:%M"
    d = datetime.strptime(date, date_format)
    return DAYS[d.weekday()]