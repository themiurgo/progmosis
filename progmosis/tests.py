import unittest

import dataio
import io

class LocationsTestCase(unittest.TestCase):
    # Location file

    locations_bad_fraction = io.StringIO(u"""datetime,location,infected_fraction
    2014-01-01,Italy,0
    2014-01-01,France,0
    2014-01-10,Italy,10
    2014-01-12,France,5""")

    locations_good_fraction = io.StringIO(u"""datetime,location,infected_fraction
    2014-01-01,Italy,0
    2014-01-01,France,0
    2014-01-10,Italy,0.01
    2014-01-12,France,0.005""")

    locations_bad_date = io.StringIO(u"""datetime,location,infected_fraction
    2014-01-01,Italy,0
    2014-13-01,France,0
    2014-01-10,Italy,0.01
    2014-01-12,France,0.005""")

    def test_locations(self):
        self.assertRaises(ValueError, dataio.parse_location, self.locations_bad_date)
        self.assertRaises(ValueError, dataio.parse_location, self.locations_bad_fraction)

if __name__ == '__main__':
    unittest.main()