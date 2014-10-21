"""progmosis. Individual risk-assessment for disease outbreaks from CDRs.

Usage:
  progmosis <regions> <movement> <calls>
  progmosis (-h | --help)
  progmosis --version

Arguments:
  <locations>     Locations file, defines how risk evolves in each place
  <movement>    Movement file, describes how people move
  <calls>       Calls file, describes how people call each other

Options:
  -h --help     Show this screen.
  --version -v  Show version.

The locations file specifies how the fraction of infected people in each
region evolves over time.

    datetime,location,infected_fraction

`infected_fraction` must be between 0 and 1.

The movement file specifies how people move between locations. It is a CSV
file with the following columns (in no particular order, header mandatory).

    datetime,user,location

`datetime` can be specified in the format "YYYY-MM-DD" and "YYYY-MM-DD HH:MM",
depending on the time resolution that is chosen.

"""
from docopt import docopt

__version__ = "0.0.1.dev1"
__author__ = "Antonio Lima"
__license__ = "MIT"
__copyright__ = 'Copyright 2014 Antonio Lima'


def main():
    arguments = docopt(__doc__, version="progmosis "+__version__)
    print(arguments)