"""progmosis. Individual risk-assessment for disease outbreaks from CDRs.

Usage:
  progmosis <global_history> <cdrs>
  progmosis (-h | --help)
  progmosis --version

Options:
  -h --help     Show this screen.
  --version -v  Show version.

"""
from docopt import docopt

__version__ = "0.0.1.dev1"
__author__ = "Antonio Lima"
__license__ = "MIT"
__copyright__ = 'Copyright 2014 Antonio Lima'


def main():
    arguments = docopt(__doc__, version="progmosis "+__version__)
    print(arguments)