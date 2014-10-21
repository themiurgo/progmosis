import collections
import csv
import dateutil.parser

def parse_location(input_fobj):
    """Parse location and return a dict of time-ordered lists of tuples.

    history[location] = [(time, infected_fraction), ...]

    input_fobj -- file object

    """

    # Convert csv to history
    reader = csv.DictReader(input_fobj)
    history = collections.defaultdict(list)
    for row in reader:
        row['infected_fraction'] = float(row['infected_fraction'])
        try:
            assert 0 <= row['infected_fraction'] <= 1
        except AssertionError:
            raise ValueError("Fraction must be between 0 and 1")
        dt = dateutil.parser.parse(row['datetime'])
        history[row['location']].append((dt, float(row['infected_fraction'])))

    # Sort history
    for location, location_history in history.iteritems():
        history[location] = sorted(location_history, key=lambda x: x[0])
        
    return history