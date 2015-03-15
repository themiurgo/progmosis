"""Simulator

- Move people around regions according to a history.
- Run epidemic.
- Keep track of the infection chain.

"""
from __future__ import division
import logging
import random
import sys
import profile

import itertools
import networkx as nx
import numpy as np

import collections
import datetime

#from toolz.itertoolz import 

def peek(iterable):
    iterator = iter(iterable)
    item = next(iterator)
    new_iterator = itertools.chain([item], iterator)
    return item, new_iterator

def n_children(tree, node):
    children = tree.successors(node)
    return sum((n_children(tree, child) for child in children))

logging.basicConfig( stream=sys.stderr )
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.WARNING)

class Population(object):
    def __init__(self):
        self._people = set()

    def remove(self, person):
        assert person._population == self
        self._people.remove(person)

    def add(self, person):
        assert person._population == self
        self._people.add(person)

    @property
    def people(self):
        return self._people

    @people.setter
    def people(self, iterable):
        for person in iterable:
            person.join_population(self)

class Person(object):
    def __init__(self, label=None):
        self._population = None
        self.label = label

    def join_population(self, population):
        if self._population:
            self._population.remove(self)
        self._population = population
        population.add(self)

    @property
    def population(self):
        return self._population

class SIS(object):
    """This class represents a simple SIS model, which can run on any arbitrary population.

    Once the object has been instantiated you can `run_one_round` on all the population in
    your scenario. The SIS object keeps track of who are the infected people.

    """

    def __init__(self, beta, mu):
        self.beta = beta
        self.mu = mu

        self.infected = set()
        self.infected_once = set()
        self.infected_tree = nx.MultiDiGraph()

    def run_one_round(self, population, k=20):
        beta, mu = self.beta, self.mu
        rand = random.random
        people_pop = population.people
        infected_pop = people_pop.intersection(self.infected)
        susceptible_pop = people_pop - self.infected
        # print "Infected, Susceptible", len(infected_pop), len(susceptible_pop)

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
                    #print "Here"
                    self.infected.add(susc_person)
                    self.infected_tree.add_edge(inf_person, susc_person)


        # Healing
        for person in infected_pop:
            if rand() < mu:
                self.infected.remove(person)

class Scenario(object):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError

class TwoGroupScenario(Scenario):
    def __init__(self, epidemic, p1=1, p2=0.000, p3=0.5, f3=0.05):
        # Initialize populations and people, allocate them randomly
        self.populations = {i: Population() for i in xrange(2)}
        self.people = {i: Person() for i in xrange(1000)}
        population_objs = self.populations.values()
        # # Three different behaviors:
        # - stay in 0 with 0.95
        # - stay in 1 with 0.95
        # - switch with 0.5 probability (people who bring the disease)
        def movement_stochastic(p):
            while True:
                if random.random() < p:
                    yield 0
                else:
                    yield 1

        self.movement_patterns = [movement_stochastic(p1),
             movement_stochastic(p2),
             movement_stochastic(p3)]

        self.epidemic = epidemic
        self.epidemic.infected.add(random.choice(self.people.values()))

        self.person_movements = {}
        for pid, person in self.people.iteritems():
            dice = random.random()
            if dice < f3:
                self.person_movements[pid] = self.movement_patterns[2]
            elif dice < 0.5 + f3/2:
                self.person_movements[pid] = self.movement_patterns[1]
            else:
                self.person_movements[pid] = self.movement_patterns[0]
        self.history = collections.defaultdict(list)

    def update(self):
        # Move people
        for pid, person in self.people.iteritems():
            pop_id = next(self.person_movements[pid])
            person.join_population(self.populations[pop_id])
            self.history[person].append(pop_id)

        # Infect people
        for i, population in enumerate(self.populations.itervalues()):
            self.epidemic.run_one_round(population)

class SEIR(object):
    """This class represents a simple SIS model, which can run on any arbitrary population.

    Once the object has been instantiated you can `run_one_round` on all the population in
    your scenario. The SIS object keeps track of who are the infected people.

    """

    def __init__(self, beta, gamma, sigma):
        self.beta = beta
        self.gamma = gamma
        self.sigma = sigma

        self.infected = set()
        self.exposed = set()
        self.susceptible = set()
        self.recovered = set()
        self.infected_tree = nx.MultiDiGraph()

    def run_one_round(self, population):
        beta, gamma, sigma = self.beta, self.gamma, self.sigma
        rand = random.random
        people_pop = population.people
        infected_pop = people_pop.intersection(self.infected)
        exposed_pop = people_pop.intersection(self.exposed)
        recovered_pop = people_pop.intersection(self.recovered)
        susceptible_pop = people_pop - self.infected - self.recovered - self.exposed
        #print "Population : {} {} {} {}".format(
        #        *map(len, [susceptible_pop, exposed_pop, infected_pop, recovered_pop]))

        def random_product(*args, **kwds):
            "Random selection from itertools.product(*args, **kwds)"
            pools = map(tuple, args) * kwds.get('repeat', 1)
            return tuple(random.choice(pool) for pool in pools)

        # S -> E
        probability = beta*len(infected_pop) / len(people_pop)
        #print "BETA", probability
        n_exposed = np.random.binomial(len(susceptible_pop), probability)
        #print n_exposed
        try:
            new_exposed = random.sample(susceptible_pop, n_exposed)
        except ValueError: # Sample larger than population
            print "ERR"
            new_exposed = susceptible_pop

        # E -> I
        n_infected = np.random.binomial(len(exposed_pop), sigma)
        try:
            new_infected = random.sample(exposed_pop, n_infected)
        except ValueError: # Sample larger than population
            print "ERR"
            new_infected = exposed_pop

        # I -> R
        n_recovered = np.random.binomial(len(infected_pop), gamma)
        try:
            new_recovered = random.sample(infected_pop, n_recovered)
        except ValueError: # Sample larger than population
            print "ERR"
            new_recovered = infected_pop
        #print "NEW Population {}: {} {} {}".format(
        #        map(len, [new_exposed, new_infected, new_recovered]))

        self.exposed.update(new_exposed)

        self.infected.update(new_infected)
        self.exposed.difference_update(new_infected)

        self.recovered.update(new_recovered)
        self.infected.difference_update(new_recovered)

class PeopleMover(object):
    def __init__(self, people_byid, movements, time_step=datetime.timedelta(10)):
        """Initialize the mover.

        Arguments:
          movements -- iterator which returns (timestamp, user, position)

        """
        self.current_time, self.movements = peek(movements)
        self.people_byid = people_byid
        self.time_step = time_step

    def process_next(self):
        time, movement = next(self.movements)
        until_time = time + self.time_step
        while time < until_time:
            user, time, location = next(self.movements)
            self.people_byid[person_id].join_population()

class Scenario(object):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError

class D4DScenario(object):
    def __init__(self, epidemic, movements, initial_conditions):
        # From movement patterns infer initial location
        self.populations = {i: Population() for i in xrange(1, 124)}
        self.people_byid = {}
        for user_id, location in initial_conditions:
            person = Person(user_id)
            self.people_byid[user_id] = person
            person.join_population(self.populations[pop_id])
        self.people_mover = PeopleMover(self.people_byid, movements)
        # Infect one random person
        self.epidemic.infected.add(random.choice(self.people_byid.values()))

    def update(self):
        # Movement step
        self.people_mover.process_next()

        # Epidemic step
        for i, population in enumerate(self.populations.itervalues()):
            self.epidemic.run_one_round(population)


class TwoGroupScenario(Scenario):
    def __init__(self, epidemic, p1=1.0000, p2=0.0000, p3=0.5, f3=0.05):
        # Initialize populations and people, allocate them randomly
        self.populations = {i: Population() for i in xrange(2)}
        self.people = {i: Person() for i in xrange(1000)}
        population_objs = self.populations.values()
        # # Three different behaviors:
        # - stay in 0 with 0.95
        # - stay in 1 with 0.95
        # - switch with 0.5 probability (people who bring the disease)
        def movement_stochastic(p):
            while True:
                if random.random() < p:
                    yield 0
                else:
                    yield 1

        self.movement_patterns = [movement_stochastic(p1), # Always in 0
             movement_stochastic(p2), #Always in 1
             movement_stochastic(p3) # 1 and 2
             ]

        self.epidemic = epidemic
        # Add always from the first population, to be able to repeat the
        # experiment and have sense when computing confidence intervals
        patient_zero = random.choice(self.people.values())
        self.epidemic.infected.add(patient_zero)

        self.person_movements = {}
        for pid, person in self.people.iteritems():
            # Make sure the patient zero comes from the same place
            if person == patient_zero:
                self.person_movements[pid] = self.movement_patterns[1]
                continue
            dice = random.random()
            if dice < f3:
                self.person_movements[pid] = self.movement_patterns[2]
            else:
                dice = random.random()
                if dice < 0.5:
                    self.person_movements[pid] = self.movement_patterns[1]
                else:
                    self.person_movements[pid] = self.movement_patterns[0]
        self.history = collections.defaultdict(list)

    def update(self):
        # Move people
        for pid, person in self.people.iteritems():
            pop_id = next(self.person_movements[pid])
            person.join_population(self.populations[pop_id])
            self.history[person].append(pop_id)

        # Infect people
        for i, population in enumerate(self.populations.itervalues()):
            self.epidemic.run_one_round(population)
