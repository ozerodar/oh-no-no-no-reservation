from datetime import timedelta
from types import SimpleNamespace

from flask import Flask
from flask import request, jsonify
import json

from reservation import Timetable, get_reservation_time, TimeSlot, get_first_free_parking_spot, \
    get_minimal_window_parking_spot, optimize_timetable, get_request

app = Flask(__name__)


def process_reservation_request(data):
    # data = json.loads(data_json)
    timetable = Timetable(data['winstrom']['udalost'], data)
    request = get_request(data['winstrom']['udalost'])

    print(timetable)

    spot = get_first_free_parking_spot(timetable, request)
    spot_min_window = get_minimal_window_parking_spot(timetable, request)
    if spot_min_window:
        timetable.add_reservation(spot_min_window, request)
    print(timetable)

    # request = TimeSlot("10", timedelta(hours=16, minutes=0), timedelta(hours=18, minutes=0))
    # timetable.remove_reservation('p1', request)
    # print(timetable)
    # optimized_timetable = optimize_timetable(timetable)
    # print(optimized_timetable)


@app.route('/thepostthepost/<shark_name>', methods=['GET', 'POST'])
def login(shark_name):
    if request.method == 'POST':
        return jsonify({"argument_was": shark_name})
    else:
        return jsonify({"argument_was": 'None'})


@app.route('/reserve/', methods=['GET', 'POST'])
def post_json():
    if request.method == 'POST':
        received_json = request.get_json()
        print(received_json)
        print(received_json['parking_spots'])
        timetable = process_reservation_request(received_json)
        print(received_json['parking_spots'])
        return jsonify(timetable)
    else:
        return "post_json called without POST"


@app.route('/')
def hello_world():
    return 'Hello, World!'