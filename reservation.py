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

def get_reservation_time(slot):
    """Convert time slot from a string (for example '13:00') to timedelta time format"""
    start_hours, start_minutes = slot.start.split(':')
    end_hours, end_minutes = slot.end.split(':')
    start = timedelta(hours=int(start_hours), minutes=int(start_minutes))
    end = timedelta(hours=int(end_hours), minutes=int(end_minutes))
    return start, end