import datetime
import io
import logging
import sys
import unittest

import simulator as sim
import dataio

logging.basicConfig( stream=sys.stderr )
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

class SimpleSISTestCase(unittest.TestCase):
    def setUp(self):
        self.italy = sim.Population()
        self.france = sim.Population()
        self.person1 = sim.Person()
        self.person2 = sim.Person()

    def test_simple_movement(self):
        self.person1.join_population(self.italy)
        self.assertEqual(self.person1.population, self.italy)
        self.assertEqual(self.france.people, set([]))
        self.assertEqual(self.italy.people, set([self.person1]))

        self.person1.join_population(self.france)
        self.assertEqual(self.person1.population, self.france)
        self.assertEqual(self.france.people, set([self.person1]))
        self.assertEqual(self.italy.people, set([]))

    def test_simple_infection(self):
        SIS = sim.SIS(0, 0)
        SIS.infected.add(self.person1)
        self.person1.join_population(self.italy)
        self.person2.join_population(self.italy)
        for i in xrange(0):
            SIS.run_one_round(self.italy)
        self.assertEqual(SIS.infected, set([self.person1]))

        SIS = sim.SIS(1, 0)
        SIS.infected.add(self.person1)
        SIS.run_one_round(self.italy)
        self.assertEqual(SIS.infected, set([self.person1, self.person2]))

class ComplexSISTestCase(unittest.TestCase):
    def setUp(self):
        self.italy = sim.Population()
        self.france = sim.Population()
        self.italians = [sim.Person() for _ in xrange(1000)]
        self.frenchmen = [sim.Person() for _ in xrange(1000)]

    def test_bulk_assignments(self):
        self.italy.people = self.italians
        self.france.people = self.frenchmen
        self.assertEqual(self.italy.people, set(self.italians))
        self.assertEqual(self.france.people, set(self.frenchmen))

        self.italians[0].join_population(self.france)
        self.assertEqual(self.italy.people, set(self.italians[1:]))
        self.assertEqual(self.france.people,
            set([self.italians[0]] + self.frenchmen))

    def test_contagion(self):
        self.italy.people = self.italians
        SIS = sim.SIS(0.20, 0.15)
        SIS.infected.add(self.italians[1])
        SIS.infected.add(self.italians[2])
        LOGGER.debug(len(SIS.infected))

        for i in xrange(100):
            SIS.run_one_round(self.italy, 2)
            LOGGER.debug(len(SIS.infected))
        LOGGER.info("Final number of infected: {0}".format(len(SIS.infected)))
        self.assertGreater(len(SIS.infected), 1)

        SIS.beta = 0
        for i in xrange(100):
            SIS.run_one_round(self.italy, 2)
        LOGGER.info("Final number of infected: {0}".format(len(SIS.infected)))
        self.assertLess(len(SIS.infected), 1)


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

        #self.assertEqual(dataio.parse_movement(simple), simple_output)

if __name__ == '__main__':
    unittest.main()