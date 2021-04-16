import json
from datetime import timedelta
from types import SimpleNamespace


class ParkingSpot:
    def __init__(self, parking_spot_info):
        self.name = parking_spot_info.name
        self.reservations = []

        for time_slot in parking_spot_info.reservations:
            start, end = get_reservation_time(time_slot)
            self.reservations.append({'start': start, 'end': end})

    def __str__(self):
        return self.name + ": " + ", ".join(
            [str(time['start']) + " - " + str(time['end']) for time in self.reservations])

    def get_next_time_slot(self, slot):
        next_slot = None
        for idx, time_slot in enumerate(self.reservations):
            if time_slot['start'] == slot['start'] and time_slot['end'] == slot['end']:
                next_slot = self.reservations[idx + 1] if idx < len(self.reservations) - 1 else None
        return next_slot

    def get_previous_time_slot(self, slot):
        prev_slot = None
        for idx, time_slot in enumerate(self.reservations):
            if time_slot['start'] == slot['start'] and time_slot['end'] == slot['end']:
                prev_slot = self.reservations[idx - 1] if idx > 0 else None
        return prev_slot

    def add_reservation(self, interval):
        """Insert a reservation so that the array of reservations remains sorted"""
        for idx, time_slot in enumerate(self.reservations):
            if interval['start'] <= time_slot['start']:
                self.reservations.insert(idx, interval)
                return
        self.reservations.append(interval)  # append to the end

    def remove_reservation(self, reservation):
        """Remove a reservation from the timetable"""
        for idx, time_slot in enumerate(self.reservations):
            if reservation['start'] == time_slot['start'] and reservation['end'] == time_slot['end']:
                self.reservations.remove(time_slot)
                break


class Timetable:
    def __init__(self, parking_spots):
        self.parking_spots = []
        for parking_spot in parking_spots:
            self.parking_spots.append(ParkingSpot(parking_spot))

    def __str__(self):
        """Print every parking spot and its actual reservations"""
        out_str = ""
        for parking_spot in self.parking_spots:
            out_str = out_str + str(parking_spot) + "\n"
        return out_str

    def add_reservation(self, target_parking_spot, time_interval):
        for parking_spot in self.parking_spots:
            if parking_spot.name == target_parking_spot.name:
                parking_spot.add_reservation(time_interval)

    def remove_reservation(self, reservation):
        for parking_spot in self.parking_spots:
            if parking_spot.name == reservation['spot']:
                parking_spot.remove_reservation(reservation)


def get_reservation_time(slot):
    """Convert time slot from a string (for example '13:00') to timedelta time format"""
    start_hours, start_minutes = slot.start.split(':')
    end_hours, end_minutes = slot.end.split(':')
    start = timedelta(hours=int(start_hours), minutes=int(start_minutes))
    end = timedelta(hours=int(end_hours), minutes=int(end_minutes))
    return start, end


def get_optimal_parking_spot(timetable, request):
    """Return the parking spot that maximizes usage of a parking spot capacity.
    Return None if there is no free parking spots"""
    pass


def get_minimal_window_parking_spot(timetable, request):
    """Return the parking spot which has reservations with start or end time as close to requested interval as
    possible. Return None if there is no free parking spots"""
    difference, optimal_spot, minimal_difference = None, None, None

    for parking_spot in timetable.parking_spots:
        for time_slot in parking_spot.reservations:

            previous_time_slot = parking_spot.get_previous_time_slot(time_slot)
            next_time_slot = parking_spot.get_next_time_slot(time_slot)

            # check if we the reservation can be put between the ending of the end of this time slot and the
            # beginning of the next one
            if request['start'] >= time_slot['end'] and (next_time_slot is None
                                                         or next_time_slot['start'] >= request['end']):

                difference = request['start'] - time_slot['end']
            # check if we the reservation can be put between the ending of the end of previous and the beginning of
            # this time slot
            elif request['end'] <= time_slot['start'] and (previous_time_slot is None
                                                           or previous_time_slot['end'] <= request['start']):
                difference = time_slot['start'] - request['end']

            if minimal_difference is not None and difference < minimal_difference \
                    or minimal_difference is None and difference is not None:
                optimal_spot = parking_spot
                minimal_difference = difference

    return optimal_spot


def get_first_free_parking_spot(timetable, request):
    """Return the first parking spot with free time slot for a given interval.
    Return None if there is no free parking spots"""

    for parking_spot in timetable.parking_spots:
        for time_slot in parking_spot.reservations:

            previous_time_slot = parking_spot.get_previous_time_slot(time_slot)
            next_time_slot = parking_spot.get_next_time_slot(time_slot)

            # check if we the reservation can be put after ending or before the beginning of this time slot
            if request['start'] >= time_slot['end'] and (next_time_slot is None
                                                         or next_time_slot['start'] >= request['end']):

                return parking_spot
            elif request['end'] <= time_slot['start'] and (previous_time_slot is None
                                                           or previous_time_slot['end'] <= request['start']):
                return parking_spot
    return None


if __name__ == '__main__':
    data = '{"parking_spots": [{"name": "p1", "reservations": [{"start": "10:00", "end": "13:00"}, \
                                                              {"start": "16:00", "end": "18:00"}]}, \
                               {"name": "p2", "reservations": [{"start": "9:00", "end": "10:00"},\
                                                               {"start": "15:00", "end": "16:00"}]},\
                               {"name": "p3", "reservations": [{"start": "08:00", "end": "18:00"}]}]}'

    parking_spots_timetable = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
    timetable = Timetable(parking_spots_timetable.parking_spots)
    request = {'start': timedelta(hours=14, minutes=0), 'end': timedelta(hours=15, minutes=0)}

    print()
    print(timetable)

    spot = get_first_free_parking_spot(timetable, request)
    print('request', request['start'], '-', request['end'], 'first free parking spot', spot)
    spot_min_window = get_minimal_window_parking_spot(timetable, request)
    print('request', request['start'], '-', request['end'], 'optimal parking spot', spot_min_window)
    timetable.add_reservation(spot_min_window, request)
    print(timetable)

    request = {'spot': 'p1', 'start': timedelta(hours=16, minutes=0), 'end': timedelta(hours=18, minutes=0)}
    timetable.remove_reservation(request)
    print('timetable:')
    print(timetable)
