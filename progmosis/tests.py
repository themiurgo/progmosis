import datetime
import io
import unittest

import dataio

class LocationsTestCase(unittest.TestCase):
    # Location file

    def test_locations(self):
        locations_bad_fraction = io.StringIO(u"""datetime,location,infected_fraction
        2014-01-01,Italy,0
        2014-01-01,France,0
        2014-01-10,Italy,10
        2014-01-12,France,5""")

        locations_bad_date = io.StringIO(u"""datetime,location,infected_fraction
        2014-01-01,Italy,0
        2014-13-01,France,0
        2014-01-10,Italy,0.01
        2014-01-12,France,0.005""")
        self.assertRaises(ValueError, dataio.parse_location, locations_bad_date)
        self.assertRaises(ValueError, dataio.parse_location, locations_bad_fraction)

    def test_simple(self):
        simple = io.StringIO(u"""datetime,location,infected_fraction
        2014-01-01,Italy,0
        2014-01-01,France,0
        2014-01-10,Italy,0.01
        2014-01-12,France,0.005""")

        simple_output = {
            "Italy": [(datetime.datetime(2014, 01, 01), 0), (datetime.datetime(2014, 01, 10), 0.01)],
            "France": [(datetime.datetime(2014, 01, 01), 0), (datetime.datetime(2014, 01, 12), 0.005)]
        }

        self.assertEqual(dataio.parse_location(simple), simple_output)

    def test_sorting(self):
        simple = io.StringIO(u"""datetime,location,infected_fraction
        2014-01-10,Italy,0.01
        2014-01-01,France,0
        2014-01-01,Italy,0
        2014-01-12,France,0.005""")

        simple_output = {
            "Italy": [(datetime.datetime(2014, 01, 01), 0), (datetime.datetime(2014, 01, 10), 0.01)],
            "France": [(datetime.datetime(2014, 01, 01), 0), (datetime.datetime(2014, 01, 12), 0.005)]
        }

        self.assertEqual(dataio.parse_location(simple), simple_output)

    def test_swapheaders(self):
        # todo
        pass

class MovementTestCase(unittest.TestCase):
    def test_simple(self):
        simple = io.StringIO(u"""datetime,user,location,
        2014-01-01,Antonio,Italy
        2014-01-01,Veljko,UK
        2014-01-10,Antonio,USA
        2014-01-12,Veljko,Slovenia""")

        simple_output = {
            "Antonio": [(datetime.datetime(2014, 01, 01), "Italy"), (datetime.datetime(2014, 01, 10), "USA")],
            "Veljko": [(datetime.datetime(2014, 01, 01), "UK"), (datetime.datetime(2014, 01, 12), "Slovenia")]
        }

        self.assertEqual(dataio.parse_movement(simple), simple_output)

if __name__ == '__main__':
    unittest.main()