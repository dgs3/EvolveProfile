import os
import sys
lib_path = os.path.abspath('./')
sys.path.insert(0, lib_path)

import unittest
import random
import mock

import EvolveProfile

class TesGA(unittest.TestCase):

    def setUp(self):
        self.population_size = 20
        self.profilemap = {
            'a': ['l', 1, 2, 3],
            'b': ['r', 0, 100],
            'c': ['l', 'a', 'b', 'c'],
            'd': ['r', -100, 0],
        }
        self.ga = EvolveProfile.GeneticAlgorithm(self.profilemap, self.population_size)
        for candidate in self.ga.population:
            candidate.fitness = random.randint(0, 100)

    def tearDown(self):
        self.population_size = None
        self.profilemap = None
        self.ga = None

    def test_generate_population(self):
        self.ga.cull_population()
        self.ga.generate_population()
        self.assertTrue(len(self.ga.population) == self.ga.population_size)

    def test_get_next_child_mutation(self):
        values = [.05, .9]
        def side_effect(*args, **kwargs):
            return values.pop()
        self.ga.uniform = mock.Mock(side_effect=side_effect)
        self.ga.create_child_with_mutation = mock.Mock(return_value=['this_is_a', 'mock_return'])
        self.ga.create_child_with_crossover = mock.Mock(return_value=['this_is_a', 'mock_return'])
        child = self.ga.create_next_child()
        self.ga.create_child_with_mutation.assert_called_once_with(self.ga.tournament_size)
        calls = self.ga.create_child_with_crossover.mock_calls
        self.assertTrue(len(calls) == 0)

    def test_get_next_child_crossover(self):
        values = [1, .4]
        def side_effect(*args, **kwargs):
            return values.pop()
        self.ga.uniform = mock.Mock(side_effect=side_effect)
        self.ga.create_child_with_crossover = mock.Mock(return_value=['this_is_a', 'mock_return'])
        self.ga.create_child_with_mutation = mock.Mock(return_value=['this_is_a', 'mock_return'])
        child = self.ga.create_next_child()
        self.ga.create_child_with_crossover.assert_called_once_with(self.ga.tournament_size)
        calls = self.ga.create_child_with_mutation.mock_calls
        self.assertTrue(len(calls) == 0)

    def test_get_next_child_both(self):
        values = [.05, .4]
        def side_effect(*args, **kwargs):
            return values.pop()
        self.ga.uniform = mock.Mock(side_effect=side_effect)
        self.ga.create_child_with_crossover = mock.Mock(return_value=['this_is_a', 'mock_return'])
        self.ga.create_child_with_mutation = mock.Mock(return_value=['this_is_a', 'mock_return'])
        child = self.ga.create_next_child()
        self.ga.create_child_with_crossover.assert_called_once_with(self.ga.tournament_size)
        self.ga.create_child_with_mutation.assert_called_once_with(self.ga.tournament_size)
        
    def test_create_child_with_crossover(self):
        tournament_size = 3
        child, p1, p2 = self.ga.create_child_with_crossover(tournament_size)
        child_context = child.get_contexts(child.profile)
        p1_context = p1.get_contexts(p1.profile)
        p2_context = p2.get_contexts(p2.profile)
        for context in child_context:
            self.assertTrue(context in p1_context or context in p2_context)

    def test_create_child_with_mutation(self):
        tournament_size = 3
        child, p1 = self.ga.create_child_with_mutation(tournament_size)
        child_context = child.get_contexts(child.profile)
        p1_context = child.get_contexts(p1.profile)
        difference = 0
        for context in child_context:
            if context not in p1_context:
                difference += 1
        self.assertTrue(difference == 1)

class TestGAMockPopulation(unittest.TestCase):

    def setUp(self):
        population_size = 50
        self.profilemap = {}
        self.ga = EvolveProfile.GeneticAlgorithm(self.profilemap, population_size=population_size)
        pop = []
        for i in range(population_size):
            pop.append(mock.Mock())
            pop[-1].fitness = i
        self.ga.population = pop

    def tearDown(self):
        self.profilemap = None
        self.ga = None

    def test_cull_population(self):
        self.assertTrue(len(self.ga.population) == self.ga.population_size)
        self.ga.cull_population()
        self.assertTrue(len(self.ga.population) == self.ga.population_size/2)

    def test_get_candidates(self):
        for i in range(0, 10):
            candidates = self.ga.get_candidates(i)
            self.assertEqual(i, len(candidates))
            for i in range(len(candidates)):
                for j in range(len(candidates)):
                    if not i == j:
                        self.assertFalse(candidates[i] == candidates[j])

    def test_get_best(self):
        for i in range(1, 50):
            best, candidates = self.ga.get_best(i)
            for c in candidates:
                self.assertTrue(best.fitness >= c.fitness)

    def test_tournament_selection_bad_size(self):
        cases = [len(self.ga.population), len(self.ga.population) + 1]
        for case in cases:
            with self.assertRaises(EvolveProfile.TournamentSizeError):
                self.ga.tournament_selection(case)

    def test_get_candidates_bad_size(self):
        cases = [len(self.ga.population), len(self.ga.population) + 1]
        for case in cases:
            with self.assertRaises(EvolveProfile.TournamentSizeError):
                self.ga.get_candidates(case)

    def test_tournament_selection_best_two(self):
        self.ga.population = self.ga.population[:3]
        got_members = self.ga.tournament_selection(num_candidates=2)
        for i in got_members:
            self.assertTrue(i.fitness > self.ga.population[0].fitness)
        got_members = sorted(got_members, cmp=lambda x,y: cmp(x.fitness, y.fitness))
        self.assertTrue(got_members[1].fitness > got_members[0].fitness)

if __name__ == "__main__":
    unittest.main()
