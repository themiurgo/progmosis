"""Simulator

- Move people around regions according to a history.
- Run epidemic.
- Keep track of the infection chain.

"""
from __future__ import division

import csv
import heapq
import logging
import random
import risk
import sys
import profile

import itertools
import networkx as nx
import numpy as np

import collections
import datetime

#from toolz.itertoolz import 

def binomial(a, b):
    #return int(max(a * b, 1))
    return np.random.binomial(a, b)


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
    def __init__(self, label):
        self._people = set()
        self.label = label

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
        self.populations = set()

    def infos(self):
        n_exposed_bylocation = collections.defaultdict(int)
        n_infected_bylocation = collections.defaultdict(int)
        n_recovered_bylocation = collections.defaultdict(int)
        for person in self.exposed:
            n_exposed_bylocation[person.population] += 1
        for person in self.infected:
            n_infected_bylocation[person.population] += 1
        for person in self.recovered:
            n_recovered_bylocation[person.population] += 1
        populations = self.populations

        f_infected = {}
        f_susceptible = {}
        for population in populations:
            n = len(population.people)
            e = n_exposed_bylocation[population]
            i = n_infected_bylocation[population]
            r = n_recovered_bylocation[population]
            s = n - e - i - r
            f_infected[population.label] = i / n
            f_susceptible[population.label] = s/n
        return f_infected, f_susceptible


    def run_one_round(self, population):
        self.populations.add(population)
        beta, gamma, sigma = self.beta, self.gamma, self.sigma
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
        n_exposed = binomial(len(susceptible_pop), probability)
        #print n_exposed
        try:
            new_exposed = random.sample(susceptible_pop, n_exposed)
        except ValueError: # Sample larger than population
            #LOGGER.error("ERR")
            new_exposed = susceptible_pop

        # E -> I
        n_infected = binomial(len(exposed_pop), sigma)
        try:
            new_infected = random.sample(exposed_pop, n_infected)
        except ValueError: # Sample larger than population
            #LOGGER.error("ERR")
            new_infected = exposed_pop

        # I -> R
        n_recovered = binomial(len(infected_pop), gamma)
        try:
            new_recovered = random.sample(infected_pop, n_recovered)
        except ValueError: # Sample larger than population
            LOGGER.error("ERR")
            new_recovered = infected_pop
        #print "NEW Population {}: {} {} {}".format(
        #        map(len, [new_exposed, new_infected, new_recovered]))

        self.exposed.update(new_exposed)

        self.infected.update(new_infected)
        self.exposed.difference_update(new_infected)

        self.recovered.update(new_recovered)
        self.infected.difference_update(new_recovered)

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return itertools.izip(a, b)

class PeopleMover(object):
    def __init__(self, people_byid, location_byid, movements, time_step=datetime.timedelta(hours=2)):
        """Initialize the mover.

        Arguments:
          movements -- iterator which returns (timestamp, user, position)

        """
        (_, self.current_time, _), self.movements = peek(movements)
        self.people_byid = people_byid
        self.location_byid = location_byid
        self.time_step = time_step
        self.inhibited = set() # People who can't move

    def inhibit(self, user_ids, locations):
        location_byid = self.location_byid
        people_byid = self.people_byid
        if locations:
            for user_id, location_id in itertools.izip(user_ids, locations):
                location = location_byid[location_id]
                people_byid[user_id].join_population(location)
        self.inhibited.update(user_ids)
        LOGGER.warning("People inhibited {}".format(len(self.inhibited)))

    def process_next(self):
        #LOGGER.warning("Movement")
        until_time = self.current_time + self.time_step
        #print until_time
        movements = self.movements
        inhibited = self.inhibited
        location_byid = self.location_byid
        people_byid = self.people_byid

        for user_id, time, location in movements:
            if time >= until_time:
                self.current_time = until_time
                self.movements = itertools.chain([(user_id, time, location)], self.movements)
                break

            user_id, time, location_id = next(movements)
            if user_id in inhibited:
            #    LOGGER.warning("Inhibited")
                continue
            #LOGGER.warning("Person {} to {}".format(user_id, location_id))
            location = location_byid[location_id]
            people_byid[user_id].join_population(location)


class Scenario(object):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError

class D4DScenario(object):
    def __init__(self, epidemic, movements, patterns, initial_conditions, intervention=None):
        if not intervention:
            intervention = "none"
        else:
            assert intervention in ("none", "random", "risk")
            if intervention == "risk":
                assert patterns

        # From movement patterns infer initial location
        self.epidemic = epidemic
        self.populations = {i: Population(i) for i in xrange(1, 124)}
        self.people_byid = {}
        for user_id, location in initial_conditions:
            person = Person(user_id)
            self.people_byid[user_id] = person
            person.join_population(self.populations[location])
        self.people_mover = PeopleMover(self.people_byid, self.populations, movements)
        #np.random.seed(12292014)
        self.random_risk = random.Random()
        #self.random_risk.seed("Risk")
        self.random_epidemic = random.Random()
        #self.random_epidemic.seed("Epidemic")
        population = self.populations[119]
        for _ in xrange(100):
            #person = random.choice(self.people_byid.values())
            person = self.random_epidemic.choice(list(population.people))
            self.epidemic.infected.add(person)
        self.patterns = patterns
        self.intervention = intervention
        self.writer = csv.writer(sys.stdout)
        self.writer.writerow(["time", "location", "susceptible", "exposed", "infected", "recovered", "total", "inhibited"])

    def update(self):
        ep = self.epidemic
        # Intervention step
        probability = 0.18#*len(ep.infected) / 140000
        #print "BETA", probability
        #n_exposed = binomial(len(ep.infected), probability)
        n_exposed = int(max(probability*len(ep.infected), 1))
        moving = set(self.people_byid.keys())
        moving.difference_update(self.people_mover.inhibited)
        moving = list(moving)
        if self.intervention == "random":
            n = n_exposed
            f_infected, f_susceptible = ep.infos()
            if f_infected and f_susceptible:
                new_inhibited = self.random_risk.sample(moving, n)
                locations = [max(self.patterns[person].iteritems(), key=lambda x: x[1])[0]
                        for person in new_inhibited]
                self.people_mover.inhibit(new_inhibited, locations)
        elif self.intervention == "risk":
            pbyid = self.people_byid
            patterns = self.patterns
            evaluate_risk = risk.evaluate_risk
            f_infected, f_susceptible = ep.infos()
            LOGGER.warning("IS {}\n{}".format(f_infected.values(), f_susceptible.values()))
            #LOGGER.warning("{} {} {}".format(moving[1] in self.patterns, moving[1], self.pattern.keys()))
            if f_infected and f_susceptible:
                risks = {user_id: evaluate_risk(patterns[user_id].items(),
                        f_infected, f_susceptible)
                    for user_id in moving
                }
                LOGGER.warning("Maximum risk: {}".format(max(risks.itervalues())))
                new_inhibited_ids = sorted(risks.iteritems(), key=lambda x: x[1], reverse=True)[:n_exposed]
                #LOGGER.warning("{}".format(new_inhibited_ids))
                new_inhibited_ids = [i[0] for i in new_inhibited_ids]
                locations = [max(self.patterns[user_id].iteritems(), key=lambda x: x[1])[0]
                        for user_id in new_inhibited_ids]
                self.people_mover.inhibit(new_inhibited_ids, locations)

        # Movement step
        self.people_mover.process_next()

        # Epidemic step
        for i, population in enumerate(self.populations.itervalues()):
            self.epidemic.run_one_round(population)

    def log(self, time_label):
        n_exposed_bylocation = collections.defaultdict(int)
        n_infected_bylocation = collections.defaultdict(int)
        n_recovered_bylocation = collections.defaultdict(int)
        ep = self.epidemic
        for person in ep.exposed:
            n_exposed_bylocation[person.population] += 1
        for person in ep.infected:
            n_infected_bylocation[person.population] += 1
        for person in ep.recovered:
            n_recovered_bylocation[person.population] += 1
        populations = ep.populations
        tot_n = 0
        writer = self.writer

        inhibited = self.people_mover.inhibited
        for population in populations:
            n = len(population.people)
            tot_n += n
            e = n_exposed_bylocation[population]
            i = n_infected_bylocation[population]
            r = n_recovered_bylocation[population]
            s = n - e - i - r
            user_ids = [p.label for p in population.people]
            ih = inhibited.intersection(user_ids)
            writer.writerow(map(str, [time_label, population.label, s, e, i, r, n, len(ih)]))
        e = len(ep.exposed)
        i = len(ep.infected)
        r = len(ep.recovered)
        n = tot_n
        s = n - e - i - r
        writer.writerow(map(str, [time_label, -1, s, e, i, r, n, len(inhibited)]))


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

        self.movement_patterns = [movement_stochastic(p1),
             movement_stochastic(p2),
             movement_stochastic(p3)]

        self.epidemic = epidemic

        self.person_movements = {}
        for pid, person in self.people.iteritems():
            dice = random.random()
            if dice < f3:
                self.person_movements[pid] = self.movement_patterns[2]
            elif dice < 0.5+f3/2:
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
