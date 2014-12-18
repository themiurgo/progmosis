from __future__ import division

import itertools
import numpy as np

def evaluate_risk(movements, f_infected, k=1):
    """Evaluate risk for a single person.

    movements -- [(time, location_i)]
    k -- number of contacts per time slot


    """

    # Convert timestamps to stay lengths
    timestamps = [i[0] for i in movements]
    places = [i[1] for i in movements]

    stays = np.diff(timestamps)

    stays_locations = zip(stays, places[:-1])
    #print stays

    risk = 0
    normalization = 1
    for (stayt1, l1), (stayt2, l2) in \
            itertools.combinations_with_replacement(stays_locations, 2):
        risk += stayt1 * stayt2 * f_infected[l1] *\
                (1 - f_infected[l2]) * k**2
        #if l1 == l2:
        #    normalization += stayt1 * stayt2 * 0.5
        #else:
        #normalization += stayt1 * stayt2
    # FIXME review normalization
    return risk / (sum(stays)**2 * len(stays)**2)

