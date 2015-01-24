from __future__ import division

import itertools
import logging
import numpy as np
import pandas as pd
import sys

import operator

logging.basicConfig( stream=sys.stderr )
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.WARNING)

def groupby_sum(iterable, key, value):
    return [(group_key, sum(value(item) for item in group))
        for group_key, group in
            itertools.groupby(sorted(iterable, key=key), key)
    ]

memoize = {}

def evaluate_risk(movements, f_infected, f_susceptible, k=1):
    """Evaluate risk for a single person.

    movements -- [(time, location_i)]
    k -- number of contacts per time slot


    """
    # Convert timestamps to stay lengths
#    timestamps, places = zip(*movements)

    #for i in list(set(places)):
    #    _ = f_infected[i]

#    stays = np.diff(timestamps).astype(float)
#    tot_stay = sum(stays)
    # Normalize stays
#    stays /= tot_stay

#    locations_stays = zip(places[:-1], stays)
#    locations_stays = groupby_sum(locations_stays, lambda x: x[0], lambda x: x[1])
    #print locations_stays
    locations_stays = movements

    #LOGGER.warning("RISK locationstays {}".format(locations_stays))
    risk = 0
    for (l1, stayt1), (l2, stayt2) in \
            itertools.combinations(locations_stays, 2):
        f1 = f_infected[l1]
        f2 = f_infected[l2]
        s1 = f_susceptible[l1]
        s2 = f_susceptible[l2]
        a = stayt1 * stayt2 * f1 * s2 * k**2
        b = stayt1 * stayt2 * f2 * s1 * k**2
        risk += a + b

    return risk
    #LOGGER.warning("Unnormalized risk: {}".format(risk))

    try:
        normalization = memoize[tuple(f_infected.iteritems()), tuple(f_susceptible.items())]
    except KeyError:
        #LOGGER.warning("Error")
        locations = [
            max(f_susceptible.iteritems(), key=lambda x: x[1])[0],
            max(f_infected.iteritems(), key=lambda x: x[1])[0],
        ]
        L = len(locations)
        normalization = 0
        for l1, l2 in \
                itertools.combinations(locations, 2):
            f1 = f_infected[l1]
            f2 = f_infected[l2]
            s1 = f_susceptible[l1]
            s2 = f_susceptible[l2]
            a = f1 * s2 * k**2
            b = f2 * s1 * k**2
            normalization += (a+b)
        #print len(list(itertools.combinations(locations, 2)))
        normalization /= L**2 # This is time normalization
        #print risk, normalization

        memoize[tuple(f_infected.iteritems()), tuple(f_susceptible.items())] = normalization

    if normalization == 0 and risk == 0:
        return 0.0
    return risk / normalization

