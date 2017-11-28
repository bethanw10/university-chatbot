from datetime import datetime, date, timedelta

from university_chatbot import *
from university_chatbot import date_util

week_one = date(2017, 9, 25)


def get_week_number(for_date):
    difference = for_date - week_one
    return (difference.days // 7) + 1


def get_date_by_week_number(week_number, day="Monday"):
    day_number = get_weekday_number(day)
    start_date = week_one + timedelta(weeks=week_number - 1, days=day_number)
    return start_date


def get_weekday_number(day):
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    day = day.lower()

    if day not in days:
        raise ValueError(day + "is not a valid day of the week")

    return days.index(day)


# TODO Fix this
def get_next_activity_date(timetable, from_date):
    start_time = datetime.strptime(timetable.start, '%H:%M').time()
    weekday = get_weekday_number(timetable.day)

    print("Day ", from_date.weekday(), "Time", from_date.time())

    # Check if activity has already occurred this week
    if weekday < from_date.weekday() or (weekday == from_date.weekday() and start_time < from_date.time()):
        day_difference = (weekday + 7) - from_date.weekday()  # Add 7 to get next weeks activity
    else:
        day_difference = weekday - from_date.weekday()

    activity_date = from_date + timedelta(days=day_difference)
    activity_date_time = datetime.combine(activity_date, start_time)

    return activity_date_time


def get_next_activity_for_module(module_code, from_date=datetime.now(), activity=None):
    week_ranges = (Week_Range.select(Week_Range, Timetable)
                   .join(Timetable)
                   .join(Module)
                   .where((Module.code ** module_code) &
                          (Week_Range.start_week <= from_date.date()) &
                          (Week_Range.end_week >= from_date.date())
                          )
                   )

    if activity is not None:
        week_ranges = week_ranges.where(Timetable.activity ** activity)

    return get_next_activity_for_week_ranges(week_ranges, from_date)


def get_next_activity_for_course(course, year, from_date=datetime.now(), activity=None):
    week_ranges = (Week_Range.select(Week_Range, Timetable)
                   .join(Timetable)
                   .join(Module)
                   .join(Course_Module)
                   .join(Course)
                   .where((Course.name ** course) &
                          (Week_Range.start_week <= from_date.date()) &
                          (Week_Range.end_week >= from_date.date())
                          )
                   )

    if year == "1":
        week_ranges = week_ranges.where(Module.code ** "4%")
    if year == "2":
        week_ranges = week_ranges.where(Module.code ** "5%")
    if year == "3" or year == "4":
        week_ranges = week_ranges.where(Module.code ** "6%")

    if activity is not None:
        week_ranges = week_ranges.where(Timetable.activity ** activity)

    return get_next_activity_for_week_ranges(week_ranges, from_date)


def get_next_activity_for_week_ranges(week_ranges, from_date):
    # Return None if no results are found
    if len(week_ranges) == 0:
        return None, None

    earliest_activity_date = datetime.max
    earliest_activity = Timetable()

    for week_range in week_ranges:
        activity_date = get_next_activity_date(week_range.timetable, from_date)

        if activity_date < earliest_activity_date:
            earliest_activity_date = activity_date
            earliest_activity = week_range.timetable

        print(week_range.timetable.activity + " " + activity_date.strftime('%d %b %Y %I:%M%p'))

    print("Earliest: " + earliest_activity.activity + " " + earliest_activity_date.strftime('%d %b %Y %I:%M%p'))
    return earliest_activity, earliest_activity_date


def get_modules_by_course(course, year=None):
    modules = (Module.select(Module)
               .join(Course_Module)
               .join(Course)
               .where(Course.name ** course)
               .order_by(Module.code)
               )

    if year == "1":
        modules = modules.where(Module.code ** "4%")
    if year == "2":
        modules = modules.where(Module.code ** "5%")
    if year == "3" or year == "4":
        modules = modules.where(Module.code ** "6%")

    return modules


def get_semester_by_module(module_code):
    matching_module = Module.select(Module.semester).where(Module.code == module_code.upper())

    if matching_module.exists():
        return matching_module.get().semester

    return None


def get_activities_on_date(course, for_date, year):
    for_date = datetime.strptime(for_date, '%Y-%m-%d')
    day = date_util.get_day_by_number(for_date.weekday())

    activities = (Timetable.select(Timetable)
                  .join(Week_Range)
                  .switch(Timetable)
                  .join(Module)
                  .join(Course_Module)
                  .join(Course)
                  .where((Course.name ** course) &
                         (Week_Range.start_week <= for_date.date()) &
                         (Week_Range.end_week >= for_date.date()) &
                         (Timetable.day == day)
                         )
                  )

    if year == "1":
        activities = activities.where(Module.code ** "4%")
    if year == "2":
        activities = activities.where(Module.code ** "5%")
    if year == "3" or year == "4":
        activities = activities.where(Module.code ** "6%")

    return activities
