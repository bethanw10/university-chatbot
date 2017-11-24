#!/usr/bin/env python
# TODO what date is week 12 - account for holidays?
# Format date correctly
import json
import re

from flask import Flask
from flask import make_response
from flask import request

from university_chatbot import *

week_one = date(2017, 9, 25)

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = make_webhook_result(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


@app.route('/webhook', methods=['GET'])
def get_request():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))


def make_webhook_result(req):
    action = req.get("result").get("action")

    if action == 'timetabling.semester':
        module_code = req.get("result").get("parameters").get('module')

        speech = timetabling_get_semester(module_code)

    elif action == 'timetabling.next_activity_module':
        module_code = req.get("result").get("parameters").get('module')
        activity = req.get("result").get("parameters").get('activity').strip()

        speech = timetabling_get_next_activity_by_module(module_code, activity)

    elif action == 'timetabling.next_activity_course':
        course = req.get("result").get("parameters").get('course').strip()
        activity = req.get("result").get("parameters").get('activity').strip()
        year = req.get("result").get("parameters").get('year').strip()

        speech = timetabling_get_next_activity_by_course(course, year, activity)

    elif action == 'timetabling.activities_for_date':
        date = req.get("result").get("parameters").get('date')
        course = req.get("result").get("parameters").get('course').strip()
        year = req.get("result").get("parameters").get('year')

        speech = timetabling_get_activities_on_date(course, date, year)

    elif action == 'timetabling.get_course_modules':
        course = req.get("result").get("parameters").get('course').strip()
        year = req.get("result").get("parameters").get('year').strip()

        speech = timetabling_get_modules_by_course(course, year)

    elif action == 'timetabling.week_start':
        week_number = req.get("result").get("parameters").get("week").strip()
        speech = timetabling_get_week_date(week_number)

    elif action == 'timetabling.get_week_number':
        for_date = req.get("result").get("parameters").get("date").strip()
        speech = timetabling_get_week(for_date)

    elif action == 'timetabling.get_module_code':
        module = req.get("result").get("parameters").get("module")
        module_code = extract_module_code(module)

        if module_code is None:
            speech = module + "? I don't recognise that module sorry"
        else:
            speech = "It's " + module_code.upper()

    elif action == 'input.unknown':
        media_type = req.get("result").get("resolvedQuery")

        # Send a like emoji in response to any images or like events
        if media_type == "FACEBOOK_MEDIA":
            speech = "👍"
        else:
            speech = req.get("result").get("fulfillment").get("speech")

    else:
        speech = req.get("result").get("fulfillment").get("speech")

    return {
        "speech": speech,
        "displayText": speech,
        "source": "apiai-university_chatbot"
    }


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

        if activity_date.date() == datetime.today().date():
            response += " today "
        elif activity_date.date() == (datetime.today() + timedelta(days=1)).date():
            response += " tomorrow "
        else:
            response += " on the " + ordinal_strftime(activity_date)

        response += " from " + timetable.start + " - " + timetable.finishes + \
                    " in room " + timetable.room

        if timetable.lecturer:
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

        if activity_date.date() == datetime.today().date():
            response += " today "
        elif activity_date.date() == (datetime.today() + timedelta(days=1)).date():
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
    return "The" + ordinal_strftime(date) + " is in week " + str(get_week_number(date))


def timetabling_get_activities_on_date(course, date, year):
    timetables = get_activities_on_date(course, date, year)
    response = "On " + ordinal_strftime(date) + " you have "
    date = datetime.strptime(date, '%Y-%m-%d')

    if len(timetables) == 0:
        return "You don't have anything that day. Enjoy your day off!"

    elif len(timetables) == 1:
        timetable = timetables.get()
        response += "a " + timetable.activity
        response += format_activity_information(timetable, date)

    else:
        response += ": "

        for timetable in timetables:
            response += "\n"
            response += "A " + timetable.activity.lower()
            response += format_activity_information(timetable, date)

    return response


def format_activity_information(timetable, activity_date):
    response = ""

    response += " for " + timetable.module.name

    response += " from " + timetable.start + " - " + timetable.finishes + \
                " in room " + timetable.room

    if timetable.lecturer != "" and timetable.lecturer != "-":
        response += " with " + timetable.lecturer + "."
    else:
        response += "."

    return response


# Module codes have the format 1AA111
def extract_module_code(module_code):
    pattern = re.compile("\d\w{2}\d{3}")
    result = pattern.search(module_code)
    if result is None:
        return None

    return result.group()


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')
