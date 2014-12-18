"""progmosis. Individual risk-assessment for disease outbreaks from CDRs.

Usage:
  progmosis <mobility> <locations> <calls>
  progmosis (-h | --help)
  progmosis --version

Arguments:
  <mobility>    Mobility file, describes how people move
  <locations>   Locations file, defines how risk evolves in each place
  <calls>       Calls file, describes how people call each other

Options:
  -h --help     Show this screen.
  --version -v  Show version.

The locations file specifies how the fraction of infected people in each
region evolves over time.

    datetime,location,infected_fraction

`infected_fraction` must be between 0 and 1.

The mobility file specifies how people move between locations. It is a CSV
file with the following columns (in no particular order, header mandatory).

    datetime,user,location

`datetime` can be specified in the format "YYYY-MM-DD" and "YYYY-MM-DD HH:MM",
depending on the time resolution that is chosen.

"""
from docopt import docopt

import codecs
import collections
import csv
import datetime
import time
import random

from risk import *

__version__ = "0.0.1.dev1"
__author__ = "Antonio Lima"
__license__ = "MIT"
__copyright__ = 'Copyright 2014 Antonio Lima'

strptime = datetime.datetime.strptime
mktime = time.mktime

def str2ts(timestr):
    time_format = "%Y-%m-%d %H:%M:%S"
    return mktime(strptime(timestr, time_format).timetuple())

def convert_time(rows):
    for user_id, time_str, location in rows:
        yield user_id, str2ts(time_str), location

def main():
    arguments = docopt(__doc__, version="progmosis "+__version__)
    #locations = codecs.open(arguments['<locations>'])
    mobility = codecs.open(arguments['<mobility>'])
    #calls = codecs.open(arguments['<calls>'])

    mobility = convert_time(csv.reader(mobility))
    user_history = collections.defaultdict(list)
    fraction_infected = collections.defaultdict(int)
    locations = set()
    for user_id, time, location in mobility:
        user_history[user_id].append((time, location))
        locations.add(location)
        # fraction_infected[location] = random.random()

    #for user_id, user_mobility in user_history.iteritems():
    #    print [i[1] for i in user_mobility]

    fraction_infected['72'] = 1

    for user_id, user_mobility in user_history.iteritems():
        a = [i[1] for i in user_mobility]
        print user_id, evaluate_risk(user_mobility, fraction_infected, 1), set(a)
