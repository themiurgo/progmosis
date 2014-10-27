"""Simulator

- Move people around regions according to a history.
- Run epidemic.
- Keep track of the infection chain.

"""
import logging
import random
import sys
import profile

logging.basicConfig( stream=sys.stderr )
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.WARNING)

class Population(object):
    def __init__(self):
        self._people = set()

    def remove(self, person):
        self._people.remove(person)

    def add(self, person):
        self._people.add(person)

    @property
    def people(self):
        return self._people

    @people.setter
    def people(self, iterable):
        for person in iterable:
            person.join_population(self)

class Person(object):
    def __init__(self):
        self._population = None

    def join_population(self, population):
        if self._population:
            self._population.remove(self)
        self._population = population
        population.add(self)

    @property
    def population(self):
        return self._population

class SIS(object):
    def __init__(self, beta, mu):
        self.beta = beta
        self.mu = mu

        self.infected = set()

    def run_one_round(self, population, k=20):
        beta, mu = self.beta, self.mu
        rand = random.random
        people_pop = population.people
        infected_pop = people_pop.intersection(self.infected)
        susceptible_pop = people_pop - self.infected

        def random_product(*args, **kwds):
            "Random selection from itertools.product(*args, **kwds)"
            pools = map(tuple, args) * kwds.get('repeat', 1)
            return tuple(random.choice(pool) for pool in pools)

        # Infections
        for inf_person in infected_pop:
            try:
                contacts = random.sample(susceptible_pop, k)
            except ValueError: # Sample larger than population
                contacts = susceptible_pop
            LOGGER.debug("Contacts {}".format(len(contacts)))
            for susc_person in contacts:
                if rand() < beta:
                    self.infected.add(susc_person)

        # Healing
        for person in infected_pop:
            if rand() < mu:
                self.infected.remove(person)
