from datetime import timedelta, date, datetime

# TODO: Add semester 3
semester_1_week_1 = date(2017, 9, 25)
semester_2_week_1 = date(2018, 1, 22)
semester_3_week_1 = date(2018, 5, 21)


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


def get_date_by_week_number(week_number, semester, day="Monday"):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    if day not in days:
        raise ValueError(day + "is not a valid day of the week")

    day_number = days.index(day)

    if semester == '1':
        start_date = semester_1_week_1
    elif semester == '2':
        start_date = semester_2_week_1
    elif semester == '3':
        start_date = semester_3_week_1
    else:
        start_date = datetime.today().date()

    if start_date < semester_2_week_1:
        start_date = semester_1_week_1 + timedelta(weeks=week_number - 1, days=day_number)
    elif start_date < semester_3_week_1:
        start_date = semester_2_week_1 + timedelta(weeks=week_number - 1, days=day_number)
    else:
        start_date = semester_3_week_1 + timedelta(weeks=week_number - 1, days=day_number)

    return start_date


def get_day_by_number(number):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return days[number]


def get_week_number(for_date):
    if type(for_date) is str:
        for_date = datetime.strptime(for_date, '%Y-%m-%d').date()

    if for_date < semester_2_week_1:
        difference = for_date - semester_1_week_1
        semester = 1
    elif for_date < semester_3_week_1:
        difference = for_date - semester_2_week_1
        semester = 2
    else:
        difference = for_date - semester_3_week_1
        semester = 3

    return semester, 1 + (difference.days // 7)
