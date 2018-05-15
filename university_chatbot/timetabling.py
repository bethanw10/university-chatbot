from university_chatbot import *
from university_chatbot import models
from university_chatbot import date_util
from datetime import datetime, timedelta


def get_weekday_number(day):
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    day = day.lower()

    if day not in days:
        raise ValueError(day + "is not a valid day of the week")

    return days.index(day)


def get_next_activity_date(week_range, from_date):
    timetable = week_range.timetable
    end_time = datetime.strptime(timetable.finishes, '%H:%M').time()
    weekday = get_weekday_number(timetable.day)
    start_week = datetime.strptime(week_range.start_week, '%Y-%m-%d')

    print("Day ", from_date.weekday(), "Time", from_date.time())

    # If timetable hasn't started yet
    if start_week >= from_date:
        activity_date = start_week + timedelta(days=weekday)
        activity_date_time = datetime.combine(activity_date, end_time)

        return activity_date_time

    else:
        # Check if activity has already occurred this week
        if weekday < from_date.weekday() or (weekday == from_date.weekday() and end_time > from_date.time()):
            day_difference = (weekday + 7) - from_date.weekday()  # Add 7 to get next weeks activity
        else:
            day_difference = weekday - from_date.weekday()  # Get this week's activity

        activity_date = from_date + timedelta(days=day_difference)
        activity_date_time = datetime.combine(activity_date, end_time)

        return activity_date_time


def get_next_activity_for_module(module_code, from_date=datetime.now(), activity=None):
    week_ranges = (Week_Range.select(Week_Range, Timetable)
                   .join(Timetable)
                   .join(Module)
                   .where((Module.code ** module_code) &
                          # (Week_Range.start_week <= from_date.date()) &
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
                          # (Week_Range.start_week <= from_date.date()) &
                          (Week_Range.end_week >= from_date.date())
                          )
                   )

    if year == "1":
        week_ranges = week_ranges.where(Module.code ** "4%")
    if year == "2":
        week_ranges = week_ranges.where(Module.code ** "5%")
    if year == "3":
        week_ranges = week_ranges.where(Module.code ** "6%")
    if year == "4":
        week_ranges = week_ranges.where(Module.code ** "7%")

    if activity is not None:
        week_ranges = week_ranges.where(Timetable.activity ** activity)

    print(week_ranges.sql())

    return get_next_activity_for_week_ranges(week_ranges, from_date)


def get_next_activity_for_week_ranges(week_ranges, from_date):
    # Return None if no results are found
    if len(week_ranges) == 0:
        return None, None

    earliest_activity_date = datetime.max
    earliest_activity = Timetable()

    # Loop through all to find the earliest activity
    for week_range in week_ranges:
        activity_date = get_next_activity_date(week_range, from_date)

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


def get_activities_on_date(course, year, for_date, activity=''):
    if type(for_date) is str:
        for_date = datetime.strptime(for_date, '%Y-%m-%d')

    if type(for_date) is datetime:
        try:
            for_date = for_date.date()
        except:
            pass

    day = date_util.get_day_by_number(for_date.weekday())

    activities = (Timetable.select(Timetable, Module)
                  .join(Week_Range)
                  .switch(Timetable)
                  .join(Module)
                  .join(Course_Module)
                  .join(Course)
                  .where((Course.name ** course) &
                         (Week_Range.start_week <= for_date) &
                         (Week_Range.end_week >= for_date) &
                         (Timetable.day == day)
                         )
                  )

    if activity is not '':
        activities = activities.where(Timetable.activity ** activity)

    if year == "1":
        activities = activities.where(Module.code ** "4%")
    if year == "2":
        activities = activities.where(Module.code ** "5%")
    if year == "3":
        activities = activities.where(Module.code ** "6%")
    if year == "4":
        activities = activities.where(Module.code ** "7%")

    return activities


def get_activities_for_date_range(course, year, start_date, end_date, activity=''):
    activities = {}

    one_day = timedelta(days=1)

    while start_date <= end_date:
        activities[start_date] = get_activities_on_date(course, year, start_date, activity)
        start_date += one_day

    return activities


def get_module_name(module_code):
    try:
        module = Module.get(Module.code == module_code)
        return module.name

    except DoesNotExist:
        return ""


def get_modules_by_lecturer(lecturer):
    if lecturer is None or lecturer == "":
        return []

    modules = (Module.select(Module)
               .distinct(True)
               .join(Timetable)
               .where(Timetable.lecturer ** (lecturer + "%"))
               )

    return modules


def get_lecturer_by_module(module_code):
    timetables = Timetable.select(Timetable) \
        .join(Module) \
        .where(Module.code == module_code)

    lecturers = [timetable.lecturer.strip() for timetable in timetables
                 if timetable.lecturer != '-' and timetable.lecturer != '']

    return list(set(lecturers))
