from datetime import timedelta, date, datetime

week_one = date(2017, 9, 25)


def suffix(day):
    if 11 <= day <= 13:
        return 'th'
    else:
        suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
        return suffixes.get(day % 10, 'th')


def ordinal_strftime(t):
    if type(t) is str:
        t = datetime.strptime(t, '%Y-%m-%d').date()

    time = t.strftime('{S} of %B %Y')
    return time.replace('{S}', str(t.day) + suffix(t.day))


def get_date_by_week_number(week_number, day="Monday"):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    if day not in days:
        raise ValueError(day + "is not a valid day of the week")

    day_number = days.index(day)

    start_date = week_one + timedelta(weeks=week_number - 1, days=day_number)
    return start_date


def get_day_by_number(number):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return days[number]


def get_week_number(for_date):
    if type(for_date) is str:
        for_date = datetime.strptime(for_date, '%Y-%m-%d').date()

    difference = for_date - week_one
    return 1 + (difference.days // 7)
