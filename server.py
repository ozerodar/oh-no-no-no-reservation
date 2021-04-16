from datetime import timedelta
from types import SimpleNamespace

from flask import Flask
from flask import request, jsonify
import json

from reservation import Timetable, get_reservation_time, TimeSlot, get_first_free_parking_spot, \
    get_minimal_window_parking_spot, optimize_timetable

app = Flask(__name__)


def my_super_post_method(data):
    # data = json.loads(data_json, object_hook=lambda d: SimpleNamespace(**d))
    timetable = Timetable(data['parking_spots'])
    start, end = get_reservation_time(data['request']['time'])
    request = TimeSlot(data['request']['user'], start, end)

    # spot = get_first_free_parking_spot(timetable, request)
    spot_min_window = get_minimal_window_parking_spot(timetable, request)
    timetable.add_reservation(spot_min_window, request)
    print(timetable)

    # request = TimeSlot("10", timedelta(hours=16, minutes=0), timedelta(hours=18, minutes=0))
    # timetable.remove_reservation('p1', request)
    # print(timetable)
    optimized_timetable = optimize_timetable(timetable)
    print(optimized_timetable)
    return optimized_timetable

@app.route('/thepostthepost/<shark_name>', methods=['GET', 'POST'])
def login(shark_name):
    if request.method == 'POST':
        return jsonify({"argument_was": shark_name})
    else:
        return jsonify({"argument_was": 'None'})


@app.route('/postjson/', methods=['GET', 'POST'])
def post_json():
    if request.method == 'POST':
        received_json = request.get_json()
        my_super_post_method(received_json)
        print(received_json['parking_spots'])
        return jsonify({"json_arg": "stuff"})
    else:
        return "post_json called without POST"

@app.route('/')
def hello_world():
    return 'Hello, World!'