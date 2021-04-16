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
