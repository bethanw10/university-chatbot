#!/usr/bin/env python
import json

from flask import Flask
from flask import make_response
from flask import request

from university_chatbot import *

session_data = {}

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


def check_session_data(session, course, year):
    if course is None or year is None:
        if session not in session_data:
            return session_data[session]
        else:
            return "", ""
    else:
        if session not in session_data:
            session_data[session] = (course, year)
        return course, year


def make_webhook_result(req):
    action = req.get("result").get("action")
    session = req.get("sessionId")

    data = ""
    contextOut = ""
    speech = req.get("result").get("fulfillment").get("speech")

    if action == 'timetabling.semester':
        module_code = req.get("result").get("parameters").get('module')

        speech = timetabling_get_semester(module_code)

    elif action == 'timetabling.next_activity_module':
        module_code = req.get("result").get("parameters").get('module')
        activity = req.get("result").get("parameters").get('activity').strip()

        speech = timetabling_get_next_activity_by_module(module_code, activity)

    elif action == 'timetabling.next_activity_course':
        course = req.get("result").get("parameters").get('course').strip()
        year = req.get("result").get("parameters").get('year').strip()
        activity = req.get("result").get("parameters").get('activity').strip()
        course, year = check_session_data(session, course, year)

        speech = timetabling_get_next_activity_by_course(course, year, activity)

    elif action == 'timetabling.activities_for_date':
        date = req.get("result").get("parameters").get('date')
        course = req.get("result").get("parameters").get('course').strip()
        year = req.get("result").get("parameters").get('year')
        course, year = check_session_data(session, course, year)

        speech = timetabling_get_activities_on_date(course, date, year)

    elif action == 'timetabling.get_course_modules':
        course = req.get("result").get("parameters").get('course').strip()
        year = req.get("result").get("parameters").get('year').strip()
        course, year = check_session_data(session, course, year)

        if course == "" or year == "":
            data = "course"
        else:
            speech = timetabling_get_modules_by_course(course, year)

    elif action == 'timetabling.week_start':
        week_number = req.get("result").get("parameters").get("week").strip()
        speech = timetabling_get_week_date(week_number)

    elif action == 'timetabling.get_week_number':
        for_date = req.get("result").get("parameters").get("date").strip()

        if for_date == "today":
            for_date = datetime.today().date()

        speech = timetabling_get_week(for_date)

    elif action == 'timetabling.get_module_code':
        module_param = req.get("result").get("parameters").get("module")
        module_code = extract_module_code(module_param)

        if module_code is None:
            speech = module_param + "? I don't recognise that module sorry"
        else:
            speech = "It's " + module_code.upper()

    elif action == 'timetabling.get_modules_by_lecturer':
        lecturer = req.get("result").get("parameters").get("lecturer")
        speech = timetable_get_modules_by_lecturer(lecturer)

    elif action == 'input.unknown':
        message = req.get("result").get("resolvedQuery")

        # Send a like emoji in response to any images or like events
        if message == "FACEBOOK_MEDIA":
            speech = "👍"
        else:
            # Search the uni website for information instead
            links = search_uni_website(message)

            if links is not None:
                speech = "I can't answer that myself sorry, but I did find some links " \
                         "that might help on the university website:\n"
                messages = [{"type": 0,
                             "speech": speech}]

                for link in links:
                    speech += link + "\n"
                    messages.append({"type": 0, "speech": link + "\n"})

                return {
                    "speech": speech,
                    "messages": messages,
                    "source": "apiai-university_chatbot"
                }

    return {
        "speech": speech,
        "displayText": speech,
        "source": "apiai-university_chatbot"
        # ,
        # "data": data,
        # "contextOut": contextOut
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')
