from university_chatbot import *
import re
import datetime


# TODO add module name
def timetabling_get_semester(module_code):
    module_code = extract_module_code(module_code)
    if module_code is None:
        return "Sorry but I couldn't find any information for that module"

    semester = get_semester_by_module(module_code)
    if semester is None:
        return "Sorry, but I couldn't find any information for " + module_code.upper()
    elif semester == "Year Long":
        return module_code.upper() + " is a year long module."
    else:
        return module_code.upper() + " is in " + semester.lower()


def timetabling_get_next_activity_by_module(module_code, activity):
    module_code = extract_module_code(module_code)
    if module_code is None:
        return "Sorry, but I couldn't find any information for that module"

    if activity is '':
        timetable, activity_date = get_next_activity_for_module(module_code)
    else:
        timetable, activity_date = get_next_activity_for_module(module_code, activity=activity)

    # TODO specify whether the module doesn't exist or if there's no more activities
    module_code = module_code.upper()

    if timetable is None:
        if activity is '':
            return "It looks like " + module_code + " doesn't have any else scheduled for the rest of the year"
        else:
            return "There aren't any more " + activity + "s" + " for " + module_code

    else:
        if activity:
            response = "The next " + activity + " for " + module_code + " is "

        else:
            response = "Next for " + module_code + " is the " + timetable.activity.lower()

        if activity_date.date() == datetime.datetime.today().date():
            response += " today "
        elif activity_date.date() == (datetime.datetime.today() + timedelta(days=1)).date():
            response += " tomorrow "
        else:
            response += " on the " + ordinal_strftime(activity_date)

        response += " from " + timetable.start + " - " + timetable.finishes + \
                    " in room " + timetable.room

        if timetable.lecturer != "" and timetable.lecturer != "-":
            response += " with " + timetable.lecturer + "."
        else:
            response += "."

        if activity is 'assessment':
            response += "Good luck with your assessment!"

        return response


def timetabling_get_next_activity_by_course(course, year, activity):
    if activity is '':
        timetable, activity_date = get_next_activity_for_course(course, year)
    else:
        timetable, activity_date = get_next_activity_for_course(course, year, activity=activity)

    # TODO specify whether the course doesn't exist or if there's no more activities
    if timetable is None:
        if activity is '':
            return "It looks like " + course + " doesn't have any else scheduled for the rest of the year"
        else:
            return "There aren't any more " + activity + "s" + " for " + course

    else:
        if activity:
            response = "The next " + activity + " for " + course + " is"

        else:
            response = "Next for " + course + " is the " + timetable.activity.lower()

        if activity_date.date() == datetime.datetime.today().date():
            response += " today "
        elif activity_date.date() == (datetime.datetime.today() + timedelta(days=1)).date():
            response += " tomorrow "
        else:
            response += " on the " + ordinal_strftime(activity_date)

        response += " for " + timetable.module.name

        response += " from " + timetable.start + " - " + timetable.finishes + \
                    " in room " + timetable.room

        if timetable.lecturer != "" and timetable.lecturer != "-":
            response += " with " + timetable.lecturer + "."
        else:
            response += "."

        if activity is 'assessment':
            response += "Good luck with your assessment!"

        return response


def timetabling_get_modules_by_course(course, year):
    modules = get_modules_by_course(course, year)

    response = "The modules for " + course + " are: \n"

    for module in modules:
        response += "" + module.code + " " + module.name + "\n"

    return response


def timetabling_get_week_date(week_number):
    start_date = get_date_by_week_number(int(week_number))

    if not 1 <= int(week_number) <= 39:
        return "There isn't a week " + week_number + ", the weeks start at 1 and end at 39"

    return "Week " + week_number + " starts on " + ordinal_strftime(start_date)


def timetabling_get_week(date):
    return "The " + ordinal_strftime(date) + " is in week " + str(get_week_number(date))


def timetabling_get_activities_on_date(course, date, year):
    timetables = get_activities_on_date(course, date, year)

    # Had if in past?
    response = "On " + ordinal_strftime(date) + " you have"

    if len(timetables) == 0:
        return "You don't have anything that day. Enjoy your day off!"

    elif len(timetables) == 1:
        timetable = timetables.get()
        response += " a " + timetable.activity
        response += format_activity_information(timetable)

    else:
        response += ": "

        for timetable in timetables:
            response += "\n"
            response += "A " + timetable.activity.lower()
            response += format_activity_information(timetable)

    return response


def format_activity_information(timetable):
    response = ""

    response += " for " + timetable.module.name

    response += " from " + timetable.start + " - " + timetable.finishes + \
                " in room " + timetable.room

    if timetable.lecturer != "" and timetable.lecturer != "-":
        response += " with " + timetable.lecturer + "."
    else:
        response += "."

    return response


def timetable_get_modules_by_lecturer(lecturer):
    modules = get_modules_by_lecturer(lecturer)
    response = lecturer + " teaches: \n"

    if len(modules) == 0:
        response = "I couldn't find any information for " + lecturer
    else:
        for module in modules:
            response += "" + module.code + " " + module.name + "\n"

    return response


# Module codes have the format 1AA111
def extract_module_code(module_code):
    pattern = re.compile("\d\w{2}\d{3}")
    result = pattern.search(module_code)
    if result is None:
        return None

    return result.group()
