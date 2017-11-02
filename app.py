#!/usr/bin/env python

import json
import os
import sqlite3

from flask import Flask
from flask import make_response
from flask import request

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

    res = make_webhook_result(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def make_webhook_result(req):
    action = req.get("result").get("action")

    if action == 'timetabling.semester':
        module_code = req.get("result").get("parameters").get('module')
        speech = timetabling_get_semester(module_code)

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
        "source": "apiai-university-chatbot"
    }


def timetabling_get_semester(module_code):
    semester = get_semester_by_module(module_code)
    if semester is None:
        return "I couldn't find any information for " + module_code
    elif semester == "Year Long":
        return "Module " + module_code + " is a year long module."
    else:
        return "Module " + module_code + " is in " + semester.lower()


def get_semester_by_module(module_code):
    db = sqlite3.connect('data/db.sqlite')
    cursor = db.cursor()
    cursor.execute("SELECT semester from module where code = '?'", [module_code.upper()])

    result = cursor.fetchone()

    if result is None:
        return None

    return result[0]


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')
