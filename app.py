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
    speech = req.get("result").get("fulfillment").get("speech")

    if action == 'timetabling.module_semester':
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

        speech = timetabling_get_next_activity_by_course(course, year, activity)

    elif action == 'timetabling.activities_for_date':
        date = req.get("result").get("parameters").get('date')
        course = req.get("result").get("parameters").get('course').strip()
        year = req.get("result").get("parameters").get('year')

        speech = timetabling_get_activities_on_date(course, year, date)

    elif action == 'timetabling.get_course_modules':
        course = req.get("result").get("parameters").get('course').strip()
        year = req.get("result").get("parameters").get('year').strip()

        speech = timetabling_get_modules_by_course(course, year)

    elif action == 'timetabling.week_start':
        week_number = req.get("result").get("parameters").get("week").strip()
        semester = req.get("result").get("parameters").get("semester").strip()
        speech = timetabling_get_week_date(week_number, semester)

    elif action == 'timetabling.get_week_number':
        for_date = req.get("result").get("parameters").get("date").strip()

        if for_date == "today":
            for_date = datetime.datetime.today().date()

        speech = timetabling_get_week(for_date)

    elif action == 'timetabling.get_week_number_period':
        date_period = req.get("result").get("parameters").get("date-period").strip()

        for_date = date_period.split("/")[0]

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

    elif action == 'timetabling.timetable':
        course = req.get("result").get("parameters").get('course').strip()
        year = req.get("result").get("parameters").get('year').strip()
        date_period = req.get("result").get("parameters").get('date-period').strip()
        activity = req.get("result").get("parameters").get('activity').strip()

        speech = timetable_get_timetable(course, year, date_period, activity)

    elif action == 'timetabling.get_lecturer':
        module_param = req.get("result").get("parameters").get('module').strip()
        module_code = extract_module_code(module_param)
        speech = timetable_get_lecturer(module_code)

    elif action == 'timetabling.timetable_by_week':
        course = req.get("result").get("parameters").get('course').strip()
        year = req.get("result").get("parameters").get('year').strip()
        week = req.get("result").get("parameters").get('week').strip()
        semester = req.get("result").get("parameters").get('semester').strip()

        speech = timetable_get_timetable_by_week(course, year, week, semester)

    elif action == 'timetabling.get_holiday':
        holiday = req.get("result").get("parameters").get('holiday').strip()
        speech = timetable_get_holiday(holiday)

    elif action == 'timetabling.courses':
        speech = timetable_get_courses()

    elif action == 'timetabling.semester':
        speech = timetable_get_semester()

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
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')
