import copy
import datetime
import json
from datetime import timedelta


class TimeSlot:
    def __init__(self, id, user, start, end):
        self.id = id
        self.user = user
        self.start = start
        self.end = end


class ParkingSpot:
    def __init__(self, name, reservable, reservations=None):
        self.name = name
        self.reservations = []

        if reservable:
            self.is_reservable = True
        else:
            self.is_reservable = False

        if reservations is not None:
            for time_slot in reservations:
                start, end = get_reservation_time(time_slot['start'], time_slot['end'])
                self.reservations.append(TimeSlot(time_slot['id'], time_slot['user'], start, end))

    def __str__(self):
        return self.name + ": " + ", ".join(
            [str(time.start) + " - " + str(time.end) + " (user " + time.user + ")" for time in self.reservations])

    def get_next_time_slot(self, slot):
        next_slot = None
        for idx, time_slot in enumerate(self.reservations):
            if time_slot.start == slot.start and time_slot.end == slot.end:
                next_slot = self.reservations[idx + 1] if idx < len(self.reservations) - 1 else None
        return next_slot

    def get_previous_time_slot(self, slot):
        prev_slot = None
        for idx, time_slot in enumerate(self.reservations):
            if time_slot.start == slot.start and time_slot.end == slot.end:
                prev_slot = self.reservations[idx - 1] if idx > 0 else None
        return prev_slot

    def add_reservation(self, interval):
        """Insert a reservation so that the array of reservations remains sorted"""
        for idx, time_slot in enumerate(self.reservations):
            if interval.start <= time_slot.start:
                self.reservations.insert(idx, interval)
                return
        self.reservations.append(interval)  # append to the end

    def remove_reservation(self, reservation):
        """Remove a reservation from the old_timetable"""
        for idx, time_slot in enumerate(self.reservations):
            if reservation.start == time_slot.start and reservation.end == time_slot.end:
                self.reservations.remove(time_slot)
                break


class Timetable:
    def __init__(self, reservations=None, json_data=None):
        self.parking_spots = []
        self.original_json = json_data
        reservable_spots = None

        if reservations:
            for element in reservations:
                if element['predmet'] == "":
                    if 'reservation' in element.keys():
                        reservable_spots = []
                        for spot in element['reservation']:
                            reservable_spots.append(spot)

        for i in range(101, 121):
            if reservable_spots is not None and str(i) in reservable_spots:
                self.parking_spots.append(ParkingSpot(str(i), True))  # TODO: add reservability info
            elif reservable_spots is not None:
                self.parking_spots.append(ParkingSpot(str(i), False))
            else:
                self.parking_spots.append(ParkingSpot(str(i), True))

        if reservations is not None:
            for reservation_info in reservations:
                # print(reservation_info)
                for spot in self.parking_spots:
                    if spot.name == reservation_info['predmet']:
                        start, end = get_reservation_time(reservation_info['zahajeni'], reservation_info['dokonceni'])
                        spot.add_reservation(TimeSlot(reservation_info['id'], reservation_info['zodpPrac'], start, end))

    def __str__(self):
        """Print every parking spot and its actual reservations"""
        out_str = "timetable:\n"
        for parking_spot in self.parking_spots:
            out_str = out_str + str(parking_spot) + "\n"
        return out_str

    def add_reservation(self, target_parking_spot, time_interval):
        for parking_spot in self.parking_spots:
            if parking_spot.name == target_parking_spot.name:
                parking_spot.add_reservation(time_interval)

    def remove_reservation(self, spot_name, interval):
        for parking_spot in self.parking_spots:
            if parking_spot.name == spot_name:
                parking_spot.remove_reservation(interval)

    def add_parking_spot(self, parking_spot):
        self.parking_spots.append(parking_spot)

    def get_spot_with_earliest_time_slot(self):
        earliest_start = timedelta(hours=99999, minutes=0)
        spot, earliest_time_slot = None, None
        for parking_spot in self.parking_spots:
            if parking_spot.is_reservable and len(parking_spot.reservations) > 0 and parking_spot.reservations[0].start <= earliest_start:
                earliest_start = parking_spot.reservations[0].start
                spot = parking_spot
                earliest_time_slot = spot.reservations[0]
        return spot, earliest_time_slot

    def get_spot_with_closest_time_slot(self, input_time_slot):
        """Get the spot with reservation that is closest to a given time slot"""
        smallest_difference = timedelta(hours=99999, minutes=0)
        spot, closest_time_slot = None, None
        for parking_spot in self.parking_spots:
            for time_slot in parking_spot.reservations:
                difference = time_slot.start - input_time_slot.end
                if parking_spot.is_reservable and time_slot.start >= input_time_slot.end and difference < smallest_difference:
                    spot = parking_spot
                    closest_time_slot = time_slot
                    smallest_difference = difference
        return spot, closest_time_slot

    def to_json(self):
        data = copy.deepcopy(self.original_json)

        for parking_spot in self.parking_spots:
            for time_slot in parking_spot.reservations:
                id = time_slot.id
                for element in data['winstrom']['udalost']:
                    if element['id'] == id:
                        element['predmet'] = parking_spot.name

                # reservations.append({"user": time_slot.user, "start": str(time_slot.start), "end": str(time_slot.end)})
            # data['parking_spots'].append({"name": parking_spot.name, "reservable": parking_spot.is_reservable, "reservations": reservations})
        return data


def convert_date_to_time(date_time):
    """Convert time slot from a string (for example '2021-04-13T10:41:49.285+02:00') to timedelta time format"""
    ref_date = datetime.date(2021, 4, 17)  # FIXME: nestihame
    date, time_region = date_time.split('T')
    year, month, day = date.split('-')
    time, _ = time_region.split('.')
    hours, minutes, _ = time.split(':')

    date = datetime.date(int(year), int(month), int(day))
    days = date - ref_date

    return timedelta(days=days.days, hours=int(hours), minutes=int(minutes))


def get_reservation_time(start_date, end_date):
    """Get start and end time of a reservation"""
    start = convert_date_to_time(start_date)
    end = convert_date_to_time(end_date)
    return start, end


def get_minimal_window_parking_spot(timetable, request):
    """Return the parking spot which has reservations with start or end time as close to requested interval as
    possible. Return None if there is no free parking spots"""
    difference, optimal_spot, minimal_difference = None, None, None

    for parking_spot in timetable.parking_spots:
        if not parking_spot.is_reservable:
            continue
        for time_slot in parking_spot.reservations:

            previous_time_slot = parking_spot.get_previous_time_slot(time_slot)
            next_time_slot = parking_spot.get_next_time_slot(time_slot)

            # check if we the reservation can be put between the ending of the end of this time slot and the
            # beginning of the next one
            if request.start >= time_slot.end and (next_time_slot is None
                                                   or next_time_slot.start >= request.end):

                difference = request.start - time_slot.end
            # check if we the reservation can be put between the ending of the end of previous and the beginning of
            # this time slot
            elif request.end <= time_slot.start and (previous_time_slot is None
                                                     or previous_time_slot.end <= request.start):
                difference = time_slot.start - request.end

            if minimal_difference is not None and difference < minimal_difference \
                    or minimal_difference is None and difference is not None:
                optimal_spot = parking_spot
                minimal_difference = difference

        # there is a possibility that there is no reservations on a spot
        if len(parking_spot.reservations) == 0 and optimal_spot is None:
            optimal_spot = parking_spot
    return optimal_spot


def get_first_free_parking_spot(timetable, request):
    """Return the first parking spot with free time slot for a given interval.
    Return None if there is no free parking spots"""

    for parking_spot in timetable.parking_spots:
        if not parking_spot.is_reservable:
            continue
        for time_slot in parking_spot.reservations:

            previous_time_slot = parking_spot.get_previous_time_slot(time_slot)
            next_time_slot = parking_spot.get_next_time_slot(time_slot)

            # check if we the reservation can be put after ending or before the beginning of this time slot
            if request.start >= time_slot.end and (next_time_slot is None
                                                   or next_time_slot.start >= request.end):

                return parking_spot
            elif request.end <= time_slot.start and (previous_time_slot is None
                                                     or previous_time_slot.end <= request.start):
                return parking_spot
    return None


def optimize_timetable(old_timetable):
    """Take a timetable and find equivalent timetable with same or lesser windows between time slots"""
    new_timetable = Timetable(json_data=old_timetable.original_json)
    for idx, parking_spot in enumerate(old_timetable.parking_spots):
        # current_parking_spot = ParkingSpot(parking_spot.name, parking_spot.is_reservable)

        if not parking_spot.is_reservable:
            for reservation in parking_spot.reservations:
                new_timetable.parking_spots[idx].add_reservation(reservation)
            for reservation in parking_spot.reservations:
                old_timetable.remove_reservation(parking_spot.name, reservation)
            continue

        earliest_start_spot, current_time_slot = old_timetable.get_spot_with_earliest_time_slot()

        if earliest_start_spot is None:
            break

        new_timetable.parking_spots[idx].add_reservation(current_time_slot)
        old_timetable.remove_reservation(earliest_start_spot.name, current_time_slot)

        while True:
            parking_spot, current_time_slot = old_timetable.get_spot_with_closest_time_slot(current_time_slot)

            if parking_spot is None:
                break

            new_timetable.parking_spots[idx].add_reservation(current_time_slot)
            old_timetable.remove_reservation(parking_spot.name, current_time_slot)
        # new_timetable.add_parking_spot(current_parking_spot)
    return new_timetable


def get_request(data):
    for element in data:
        if element['predmet'] == "":
            start, end = get_reservation_time(element['zahajeni'], element['dokonceni'])
            return TimeSlot(element['id'], element['zodpPrac'], start, end)


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
    # print(timetable)
    # print('-------')
    optimized_timetable = optimize_timetable(timetable)
    print(optimized_timetable)
    return optimized_timetable.to_json()


if __name__ == '__main__':
    # test data
    data_json = '{\
    "winstrom": {\
        "@version": "1.0",\
        "udalost": [\
            {\
                "id": "1",\
                "lastUpdate": "2021-04-17T09:42:11.397+02:00",\
                "cenik": "",\
                "firma": "",\
                "zahajeni": "2021-04-17T19:41:49.285+02:00",\
                "dokonceni": "2021-04-17T20:41:49.285+02:00",\
                "predmet": "",\
                "typAkt": "code:UDÁLOST",\
                "typAkt@ref": "/c/rezervace1/typ-aktivity/1.json",\
                "typAkt@showAs": "UDÁLOST: Událost",\
                "zodpPrac": "code:admin",\
                "zodpPrac@ref": "/c/rezervace1/uzivatel/1.json",\
                "zodpPrac@showAs": "admin",\
                "majetek": ""\
            },\
            {\
                "id": "41",\
                "lastUpdate": "2021-04-17T23:04:21.274+02:00",\
                "cenik": "",\
                "firma": "",\
                "zahajeni": "2021-04-17T11:41:49.285+02:00",\
                "dokonceni": "2021-04-17T12:41:49.285+02:00",\
                "predmet": "101",\
                "typAkt": "code:UDÁLOST",\
                "typAkt@ref": "/c/rezervace1/typ-aktivity/1.json",\
                "typAkt@showAs": "UDÁLOST: Událost",\
                "zodpPrac": "code:admin",\
                "zodpPrac@ref": "/c/rezervace1/uzivatel/1.json",\
                "zodpPrac@showAs": "admin",\
                "majetek": ""\
            },\
            {\
                "id": "42",\
                "lastUpdate": "2021-04-16T23:33:09.927+02:00",\
                "cenik": "",\
                "firma": "",\
                "zahajeni": "2021-04-17T15:41:49.285+02:00",\
                "dokonceni": "2021-04-17T16:41:49.285+02:00",\
                "predmet": "102",\
                "typAkt": "code:UDÁLOST",\
                "typAkt@ref": "/c/rezervace1/typ-aktivity/1.json",\
                "typAkt@showAs": "UDÁLOST: Událost",\
                "zodpPrac": "code:admin",\
                "zodpPrac@ref": "/c/rezervace1/uzivatel/1.json",\
                "zodpPrac@showAs": "admin",\
                "majetek": ""\
            }\
        ]\
    }}'

    process_reservation_request(json.loads(data_json))
    optimize(json.loads(data_json))
