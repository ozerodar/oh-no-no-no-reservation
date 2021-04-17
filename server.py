from datetime import timedelta
from types import SimpleNamespace

from flask import Flask
from flask import request, jsonify

from reservation import Timetable, get_reservation_time, TimeSlot, get_first_free_parking_spot, \
    get_minimal_window_parking_spot, optimize_timetable, get_request

app = Flask(__name__)


def process_reservation_request(data):
    timetable = Timetable(data['winstrom']['udalost'], data)
    request = get_request(data['winstrom']['udalost'])
    print(timetable)

    # spot = get_first_free_parking_spot(timetable, request)
    spot_min_window = get_minimal_window_parking_spot(timetable, request)
    if spot_min_window:
        timetable.add_reservation(spot_min_window, request)
    print(timetable)
    print('-------')
    # optimized_timetable = optimize_timetable(timetable)
    # print(optimized_timetable)
    return timetable.to_json()


def optimize(data):
    timetable = Timetable(data['winstrom']['udalost'], data)
    optimized_timetable = optimize_timetable(timetable)
    print(optimized_timetable)
    return optimized_timetable.to_json()


@app.route('/reserve/', methods=['GET', 'POST'])
def post_json():
    if request.method == 'POST':
        received_json = request.get_json()
        timetable = process_reservation_request(received_json)
        return jsonify(timetable)
    else:
        return "post_json called without POST"


@app.route('/optimize/', methods=['GET', 'POST'])
def post_json():
    if request.method == 'POST':
        received_json = request.get_json()
        timetable = process_reservation_request(received_json)
        return jsonify(timetable)
    else:
        return "post_json called without POST"