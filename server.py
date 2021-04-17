from datetime import timedelta
from types import SimpleNamespace

from flask import Flask
from flask import request, jsonify
from reservation import process_reservation_request, optimize

app = Flask(__name__)


@app.route('/reserve/', methods=['GET', 'POST'])
def post_json():
    if request.method == 'POST':
        received_json = request.get_json()
        print(received_json)
        timetable = process_reservation_request(received_json)
        return jsonify(timetable)
    else:
        return "post_json called without POST"


@app.route('/optimize/', methods=['GET', 'POST'])
def post_optimize():
    if request.method == 'POST':
        received_json = request.get_json()
        timetable = optimize(received_json)
        return jsonify(timetable)
    else:
        return "post_json called without POST"