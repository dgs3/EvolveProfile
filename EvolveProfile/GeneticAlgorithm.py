"""
The main genetic algorithm that breeds, culls and derives fitness
"""

from __future__ import unicode_literals, print_function

import random

import EvolveProfile

class GeneticAlgorithm(object):

    def __init__(self, profilemap, population_size, ingenomes=[]):
        self.profilemap = profilemap
        self.population_size = population_size
        self.population = ingenomes[:self.population_size]
        while len(self.population) < self.population_size:
            self.population.append(EvolveProfile.Genotype(self.profilemap))
        self.mutation_rate = .1
        self.crossover_rate = .5
        self.tournament_size = 3
        self.uniform = random.uniform

    def generate_population(self):
        """
        Creates new offspring
        """
        children = []
        while len(children) < self.population_size - len(self.population):
            children.extend(self.create_next_child())
        assert len(children) + len(self.population) == self.population_size
        self.population.extend(children)

    def create_next_child(self):
        """
        Creates new children using either the crossover or mutation operators
        """
        children = []
        if self.uniform(0, 1) < self.crossover_rate:
            children.append(self.create_child_with_crossover(self.tournament_size)[0])
        if self.uniform(0, 1) < self.mutation_rate:
            children.append(self.create_child_with_mutation(self.tournament_size)[0])
        return children

    def create_child_with_mutation(self, num_candidates):
        """
        Mutates a child.

        @param int num_candidates: The number of candidates to use when executing tournament
            selection
        @return list: 
            mutant: Mutant child
            p1: The progenitor.  Used for testing
        """
        p1 = self.get_best(num_candidates)[0]
        mutant = p1.copy()
        mutant.mutate()
        return mutant, p1

    def create_child_with_crossover(self, num_candidates):
        """
        Creates a child with crossover

        @param int num_candidates: The number of candidates to use when executing tournament
            selection
        @return list:
            progeny: Children generated with crossover
            p1, p2: The progenitors.  Used for testing.
        """
        p1, p2 = self.tournament_selection(num_candidates)
        new_profile = p1.uniform_crossover(p2)
        progeny = EvolveProfile.Genotype(self.profilemap, ingenotype=new_profile)
        return progeny, p1, p2

    def tournament_selection(self, num_candidates):
        """
        Gets two parents VIA tournament selection.

        @param int num_candidates: The number of candidates to use when executing tournament
            selection
        @return list:
            first: First chosen candidate
            second: Second chosen candidate
        """
        first = self.get_best(num_candidates)[0]
        second = self.get_best(num_candidates)[0]
        while first == second:
            second = self.get_best(num_candidates)[0]
        return first, second

    def get_best(self, num_candidates):
        """
        Given a number of candidates, get the one with the best fitness

        @param int num_candidates: The number of candidates to use when executing tournament
            selection
        @return list:
            best child: The most fit candidate
            candidates: Pool of candidates
        """
        if num_candidates == 0:
            return None, self.population
        candidates = self.get_candidates(num_candidates)
        sorted_candidates = sorted(candidates, cmp=lambda x,y: cmp(x.fitness, y.fitness))
        return sorted_candidates[-1], candidates

    def get_candidates(self, num_candidates):
        """
        Gets a set of candidates of given size

        @param int num_candidates: The number of candidates to use when executing tournament
            selection
        @return candidates: Discrete candidates
        """
        if num_candidates >= len(self.population):
            raise EvolveProfile.TournamentSizeError
        candidates = []
        new = random.choice(self.population)
        for i in range(num_candidates):
            while any(new == chosen for chosen in candidates):
                new = random.choice(self.population)
            candidates.append(new)
        return candidates 

    def cull_population(self):
        self.population = self.population[:self.population_size/2]

    def ascertain_fitness(self):
        self.fitness_calculator.ascertain_fitness(self.population)
