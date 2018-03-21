from university_chatbot import *
import re
import datetime


def timetabling_get_semester(module_code):
    module_code = extract_module_code(module_code)
    if module_code is None:
        return "Sorry but I couldn't find any information for that module"

    semester = get_semester_by_module(module_code)

    if semester is None:
        return "Sorry, but I couldn't find any information for " + module_code.upper()
    else:
        module_name = get_module_name(module_code)

        if semester == "Year Long":
            return module_code.upper() + " " + module_name + " is a year long module."
        else:
            return module_code.upper() + " " + module_name + " is in " + semester.lower()


def timetabling_get_next_activity_by_module(module_code, activity):
    module_code = extract_module_code(module_code)

    if module_code is None:
        return "Sorry, but I couldn't find any information for that module"
    if activity is '':
        timetable, activity_date = get_next_activity_for_module(module_code)
    else:
        timetable, activity_date = get_next_activity_for_module(module_code, activity=activity)

    module_code = module_code.upper()

    if timetable is None:
        module = Module.select().where(Module.code == module_code)

        if not module.exists():
            return "Sorry, but I don't have any timetable information for a module with the code " + module_code
        else:
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


def timetabling_get_next_activity_by_course(course_name, year, activity):
    if activity is '':
        timetable, activity_date = get_next_activity_for_course(course_name, year)
    else:
        timetable, activity_date = get_next_activity_for_course(course_name, year, activity=activity)

    # No activities found
    if timetable is None:
        course = Course.select().where(Course.name ** course_name)

        if not course.exists():
            return "Sorry, but I couldn't find a course named " + course_name
        else:
            if activity is '':
                return "It looks like " + course_name + " doesn't have any else scheduled for the rest of the year"
            else:
                return "There aren't any more " + activity + "s" + " for " + course_name

    else:
        if activity:
            response = "The next " + activity + " for " + course_name + " is"

        else:
            response = "Next for " + course_name + " is the " + timetable.activity.lower()

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


def timetabling_get_week_date(week_number, semester):
    if not 1 <= int(week_number) <= 12:
        return "There isn't a week " + week_number + ", the weeks start at 1 and end at 12"

    start_date = get_date_by_week_number(int(week_number), semester)

    return "Week " + week_number + " starts on " + ordinal_strftime(start_date)


def timetabling_get_week(for_date):
    semester, week_number = get_week_number(for_date)
    return "The " + ordinal_strftime(for_date) + " is in Semester " + str(semester) + " Week " + str(week_number)


def timetabling_get_activities_on_date(course, year, for_date):
    timetables = get_activities_on_date(course, year, for_date)

    for_date = datetime.datetime.strptime(for_date, '%Y-%m-%d')

    if for_date > datetime.datetime.today():
        response = "On " + ordinal_strftime(for_date) + " you have"
    else:
        response = "On " + ordinal_strftime(for_date) + " you had"

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


def timetable_get_timetable(course, year, time_period):
    if time_period == '':
        start_date = datetime.datetime.today()
        end_date = start_date + timedelta(days=7)

        response = "Your timetable for the next 7 days is:\n"

    else:
        start_and_end = time_period.split("/")
        start_date = datetime.datetime.strptime(start_and_end[0], '%Y-%m-%d')
        end_date = datetime.datetime.strptime(start_and_end[1], '%Y-%m-%d')

        response = "Your timetable for " + ordinal_strftime(start_and_end[0]) + \
                   " to " + ordinal_strftime(start_and_end[1]) + " is:\n"

    print(start_date, end_date)

    timetable = get_activities_for_date_range(course, year, start_date, end_date)

    if len(timetable) == 0:
        response = "I couldn't find any timetable information"
    else:
        for key, value in timetable.items():
            response += get_day_by_number(key.weekday()) + " " + ordinal_strftime(key) + "\n"

            if len(value) == 0:
                response += "\tNothing\n"
            else:
                for event in value:
                    # response += "\t The " + event.activity.lower() + " for " + event.module.name
                    response += "\t" + event.module.name + " " + event.activity.lower()
                    response += ", " + event.start + " - " + event.finishes + \
                                " in room " + event.room

                    if event.lecturer != "" and event.lecturer != "-":
                        response += " with " + event.lecturer + "."
                    else:
                        response += "."

                    response += "\n"

            response += "\n"

    return response


def timetable_get_lecturer(module_code):
    lecturers = get_lecturer_by_module(module_code)

    if len(lecturers) == 0:
        return "I couldn't find any lecturer details for that module code"
    elif len(lecturers) == 1:
        return "The lecturer for " + get_module_name(module_code) + " is " + lecturers[0]
    else:
        response = "The lecturers for " + get_module_name(module_code) + " are:\n"
        for lecturer in lecturers:
            response += "\t" + lecturer + "\n"

        return response


# Module codes have the format 0AA000
def extract_module_code(module_code):
    pattern = re.compile("\d\w{2}\d{3}")
    result = pattern.search(module_code)
    if result is None:
        return None

    return result.group()
