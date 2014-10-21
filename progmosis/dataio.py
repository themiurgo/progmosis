import csv
import dateutil.parser

def parse_location(text):
    reader = csv.DictReader(text)
    for row in reader:
        dateutil.parser.parse(row['datetime'])
    try:
        assert 0 <= row['infected_fraction'] <= 1
    except AssertionError:
        raise ValueError("Fraction must be between 0 and 1")