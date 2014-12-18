from __future__ import division

import itertools
import numpy as np

import operator


def groupby_sum(iterable, key, value):
    return [(group_key, sum(value(item) for item in group))
        for group_key, group in
            itertools.groupby(sorted(iterable, key=key), key)
    ]

def evaluate_risk(movements, f_infected, k=1):
    """Evaluate risk for a single person.

    movements -- [(time, location_i)]
    k -- number of contacts per time slot


    """

    # Convert timestamps to stay lengths
    timestamps = [i[0] for i in movements]
    places = [i[1] for i in movements]
    for i in list(set(places)):
        _ = f_infected[i]

    stays = np.diff(timestamps).astype(float)
    tot_stay = sum(stays)
    # Normalize stays
    stays /= tot_stay

    stays_locations = zip(places[:-1], stays)
    stays_locations = groupby_sum(stays_locations, lambda x: x[0], lambda x: x[1])
    #print stays_locations

    risk = 0
    for (l1, stayt1), (l2, stayt2) in \
            itertools.combinations(stays_locations, 2):
        f1 = f_infected[l1]
        f2 = f_infected[l2]
        a = stayt1 * stayt2 * f1 * (1-f2) * k**2
        b = stayt1 * stayt2 * f2 * (1-f1) * k**2
        risk += a + b

    locations = [
        min(f_infected.iteritems(), key=lambda x: x[1])[0],
        max(f_infected.iteritems(), key=lambda x: x[1])[0],
    ]
    L = len(locations)
    normalization = 0
    for l1, l2 in \
            itertools.combinations(locations, 2):
        f1 = f_infected[l1]
        f2 = f_infected[l2]
        a = f1 * (1-f2) * k**2
        b = f2 * (1-f1) * k**2
        normalization += (a+b)
    #print len(list(itertools.combinations(locations, 2)))
    normalization /= L**2 # This is time normalization
    #print risk, normalization

    if normalization == 0 and risk == 0:
        return 0.0

    # FIXME review normalization
    return risk / normalization

