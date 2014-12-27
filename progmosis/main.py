import csv
import gzip
import sys

import dateutil.parser

import simulator


def get_movements(fobj):
    reader = csv.reader(fobj)
    for user_id, time, location in reader:
        yield int(user_id), datutil.parser.parse(time), int(location)

def get_ic(fobj):
    reader = csv.reader(fobj)
    for user_id, time, _ in reader:
        yield int(user_id), int(location)


epidemic = simulator.SEIR(1, 1/5.61, 1/5.3)
movements = get_movements(gzip.GzipFile(sys.argv[2]))
initial_conditions = get_ic(open(sys.argv[1]))
scenario = simulator.D4DScenario(epidemic, movements, initial_conditions)
