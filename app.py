#!/usr/bin/env python

import json

from flask import Flask
from flask import make_response
from flask import request

from university_chatbot import *

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
        activity = req.get("result").get("parameters").get('activity')

        speech = timetabling_get_next_activity_by_module(module_code, activity)

    elif action == 'timetabling.next_activity_course':
        course = req.get("result").get("parameters").get('course')
        activity = req.get("result").get("parameters").get('activity')

        speech = timetabling_get_next_activity_by_course(course, activity)

    else:
        speech = action
        for keys, values in req.get("result").get("parameters").items():
            speech += "  " + values

        print("Response:")
        print(speech)
        speech = "Message type: " + speech

    return {
        "speech": speech,
        "displayText": speech,
        "source": "apiai-university_chatbot"
    }


def timetabling_get_semester(module_code):
    semester = get_semester_by_module(module_code)
    if semester is None:
        return "I couldn't find any information for " + module_code.upper()
    elif semester == "Year Long":
        return "Module " + module_code.upper() + " is a year long module."
    else:
        return "Module " + module_code.upper() + " is in " + semester.lower()


def timetabling_get_next_activity_by_module(module_code, activity):
    if activity is '':
        timetable, activity_date = get_next_activity_for_module(module_code)
    else:
        timetable, activity_date = get_next_activity_for_module(module_code, activity=activity)

    # TODO specify whether the module doesn't exist or if there's no more activities
    # & only reply with information that is there
    if timetable is None:
        if activity is '':
            return module_code + "doesn't have any else scheduled for the rest of the year"
        else:
            return "There aren't any more " + activity + "s" + " for " + module_code.upper()

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
            response += " on the " + activity_date.strftime('%A %d %b %Y')

        response += " from " + timetable.start + " - " + timetable.finishes + \
                    " in room " + timetable.room

        if timetable.lecturer:
            response += " with " + timetable.lecturer + "."
        else:
            response += "."

        return response


def timetabling_get_next_activity_by_course(course, activity):
    if activity is '':
        timetable, activity_date = get_next_activity_for_course(course)
    else:
        timetable, activity_date = get_next_activity_for_course(course, activity=activity)

    # TODO specify whether the course doesn't exist or if there's no more activities
    # & only reply with information that is there
    if timetable is None:
        if activity is '':
            return course + "doesn't have any else scheduled for the rest of the year"
        else:
            return "There aren't any more " + activity + "s" + " for " + course

    else:
        if activity:
            response = "The next " + activity + " for " + course + " is "

        else:
            response = "Next for " + course + " is the " + timetable.activity.lower()

        if activity_date.date() == datetime.today().date():
            response += " today "
        elif activity_date.date() == (datetime.today() + timedelta(days=1)).date():
            response += " tomorrow "
        else:
            response += " on the " + activity_date.strftime('%A %d %b %Y')

        response += " from " + timetable.start + " - " + timetable.finishes + \
                    " in room " + timetable.room

        if timetable.lecturer:
            response += " with " + timetable.lecturer + "."
        else:
            response += "."

        return response


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')
