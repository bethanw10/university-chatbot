from datetime import timedelta, date, datetime

semester_1_week_1 = date(2017, 9, 25)
semester_2_week_1 = date(2018, 1, 22)
semester_3_week_1 = date(2018, 5, 21)

holidays = {
    "Christmas Break": [date(2017, 12, 18), date(2018, 1, 21)],
    "Easter Break": [date(2018, 3, 26), date(2018, 4, 8)]
}


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


def get_date_by_week_number(week_number, semester='', day="Monday"):
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
        semester = get_current_semester()
        start_date = datetime.today().date()

    if start_date < semester_2_week_1:
        start_date = semester_1_week_1 + timedelta(weeks=week_number - 1, days=day_number)
    elif start_date < semester_3_week_1:
        start_date = semester_2_week_1 + timedelta(weeks=week_number - 1, days=day_number)
    else:
        start_date = semester_3_week_1 + timedelta(weeks=week_number - 1, days=day_number)

    is_holiday, _ = is_date_in_holiday(start_date)

    if is_holiday or is_date_past_holiday(int(semester), start_date):
        start_date += timedelta(weeks=2)

    return start_date


# TODO: Should probably do this a better way?
def is_date_past_holiday(semester, for_date):
    if semester == 1:
        return for_date > holidays["Christmas Break"][0]
    elif semester == 2:
        return for_date > holidays["Easter Break"][0]
    else:
        return False


def get_current_semester():
    start_date = datetime.today().date()

    if start_date < semester_2_week_1:
        return 1
    elif start_date < semester_3_week_1:
        return 2
    else:
        return 3


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

    week_number = 1 + (difference.days // 7)

    if is_date_past_holiday(int(semester), for_date):
        week_number -= 2

    return semester, week_number


def is_date_in_holiday(for_date):
    if type(for_date) is str:
        for_date = datetime.strptime(for_date, '%Y-%m-%d').date()

    for holiday, dates in holidays.items():
        # 0 is start date, 1 is end date
        if dates[0] <= for_date <= dates[1]:
            return True, holiday

    return False, ""


def get_holiday_start_date(holiday):
    if holiday in holidays:
        dates = holidays[holiday]
        return dates[0]

    # Default to closest holiday to today
    else:
        return None


def get_closest_holiday():
    nearest_holiday = None
    for holiday, dates in holidays.items():
        # 0 is start date, 1 is end date
        if datetime.today().date() < dates[0]:
            nearest_holiday = holiday, dates

    if nearest_holiday is not None:
        return nearest_holiday
    else:
        return None, None
