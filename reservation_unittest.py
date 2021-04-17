import json
import unittest
from reservation import process_reservation_request

test_data = json.loads('{\
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
    }}')

optimal_space_data = json.loads('{\
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
                "predmet": "102",\
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
    }}')


class MyTestCase(unittest.TestCase):
    def test_optimal_spot_easy(self):
        timetable = process_reservation_request(test_data)
        self.assertEqual(timetable, optimal_space_data)

    def test_if_manager_spot_can_be_reserved(self):
        timetable = process_reservation_request(test_data)
        self.assertEqual(timetable, optimal_space_data)

if __name__ == '__main__':
    unittest.main()
