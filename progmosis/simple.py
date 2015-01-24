from __future__ import division

import collections
import csv
import gzip
import itertools
import sys

import dateutil.parser

import simulator

intervention = sys.argv[2]

def get_movements(fobj):
    reader = csv.reader(fobj)
    for user_id, time, location in reader:
        yield int(user_id), dateutil.parser.parse(time), int(location)

def get_patterns(fobj):
    reader = csv.reader(fobj)
    next(reader)
    pattern = collections.defaultdict(lambda: collections.defaultdict(float))
    for user_id, location, fraction in reader:
        pattern[int(user_id)][int(location)] = float(fraction)
    return pattern

def ic(patterns):
    for user_id, loc_frac in patterns.iteritems():
        yield user_id, max(loc_frac.iteritems(), key=lambda x: x[1])[0]


minutes_day = 60*24
step = 120
step = 240
D = minutes_day / step
#assert D==12

epidemic = simulator.SEIR(0.45/D, 1/5.61/D, 1/5.3/D)
#print patterns
#sys.exit(1)
initial_conditions = ic(patterns)
scenario = simulator.TwoGroupScenario(epidemic)

for i in xrange(60*24*30*2 // step):
    scenario.update()
    scenario.log(i)
