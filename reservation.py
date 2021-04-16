import json
from datetime import timedelta
from types import SimpleNamespace


class TimeSlot:
    def __init__(self, user, start, end):
        self.user = user
        self.start = start
        self.end = end


class ParkingSpot:
    def __init__(self, name, reservable, reservations=None):
        self.name = name
        self.reservations = []

        if reservable == 'True':
            self.is_reservable = True
        else:
            self.is_reservable = False

        if reservations is not None:
            for time_slot in reservations:
                start, end = get_reservation_time(time_slot)
                self.reservations.append(TimeSlot(time_slot['user'], start, end))

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
    def __init__(self, parking_spots=None):
        self.parking_spots = []

        if parking_spots is not None:
            for parking_spot_info in parking_spots:
                self.parking_spots.append(
                    ParkingSpot(parking_spot_info['name'], parking_spot_info['reservable'], parking_spot_info['reservations']))

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
            if len(parking_spot.reservations) > 0 and parking_spot.reservations[0].start < earliest_start:
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
                if time_slot.start >= input_time_slot.end and difference < smallest_difference:
                    spot = parking_spot
                    closest_time_slot = time_slot
                    smallest_difference = difference
        return spot, closest_time_slot

    def to_json(self):
        data['parking_spots'] = []
        for parking_spot in self.parking_spots:
            reservations = []
            for time_slot in parking_spot.reservations:
                reservations.append({"user": time_slot.user, "start": time_slot.start, "end": time_slot.end})
            data['parking_spots'].append({"name": parking_spot.name, "reservable": parking_spot.is_reservable, "reservations": reservations})
        return json.dumps(data)


def get_reservation_time(slot):
    """Convert time slot from a string (for example '13:00') to timedelta time format"""
    start_hours, start_minutes = slot['start'].split(':')
    end_hours, end_minutes = slot['end'].split(':')
    start = timedelta(hours=int(start_hours), minutes=int(start_minutes))
    end = timedelta(hours=int(end_hours), minutes=int(end_minutes))
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
    new_timetable = Timetable()
    for parking_spot in old_timetable.parking_spots:
        current_parking_spot = ParkingSpot(parking_spot.name, parking_spot.is_reservable)
        earliest_start_spot, current_time_slot = old_timetable.get_spot_with_earliest_time_slot()

        if earliest_start_spot is None:
            new_timetable.add_parking_spot(current_parking_spot)
            break

        current_parking_spot.add_reservation(current_time_slot)
        old_timetable.remove_reservation(earliest_start_spot.name, current_time_slot)

        while True:
            parking_spot, current_time_slot = old_timetable.get_spot_with_closest_time_slot(current_time_slot)

            if parking_spot is None:
                break

            current_parking_spot.add_reservation(current_time_slot)
            old_timetable.remove_reservation(parking_spot.name, current_time_slot)
        new_timetable.add_parking_spot(current_parking_spot)
    return new_timetable


if __name__ == '__main__':
    data_json = '{"parking_spots": [{"name": "p1", "reservable": "True", "reservations": [{"user": "1", "start": "10:00", "end": "13:00"}, \
                                                              {"user": "2", "start": "16:00", "end": "18:00"}]}, \
                               {"name": "p2", "reservable": "True", "reservations": [{"user": "3", "start": "9:00", "end": "10:00"},\
                                                               {"user": "4", "start": "15:00", "end": "16:00"}]},\
                               {"name": "p3", "reservable": "True", "reservations": [{"user": "5", "start": "08:00", "end": "18:00"}]}],\
            "request": {"user": "55", "time":{"start": "14:00", "end": "15:00"}}}'

    data = json.loads(data_json)
    timetable = Timetable(data['parking_spots'])
    start, end = get_reservation_time(data['request']['time'])
    request = TimeSlot(data['request']['user'], start, end)

    # print(old_timetable)

    spot = get_first_free_parking_spot(timetable, request)
    # print('request', request['start'], '-', request['end'], 'first free parking spot', spot)
    spot_min_window = get_minimal_window_parking_spot(timetable, request)
    # print('request', request['start'], '-', request['end'], 'optimal parking spot', spot_min_window)
    timetable.add_reservation(spot_min_window, request)
    print(timetable)

    # request = TimeSlot("10", timedelta(hours=16, minutes=0), timedelta(hours=18, minutes=0))
    # timetable.remove_reservation('p1', request)
    # print(timetable)
    optimized_timetable = optimize_timetable(timetable)
    print(optimized_timetable)
