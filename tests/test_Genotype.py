import os
import sys
lib_path = os.path.abspath('./')
sys.path.insert(0, lib_path)

import unittest
import random

import EvolveProfile

class TestGenotype(unittest.TestCase):

    def setUp(self):
        self.profile = {
            "paramA" : ['r', 0, 100],
            "paramB" : ['l', 0, 1, 2, 3, 4, 5],
            "subConfig": {
                "paramD": ['r', 100, 200],
                "paramE": ['l', 'a', 'b', 'c', 'd'],
            }
        }
        self.genotype = EvolveProfile.Genotype(self.profile)

    def tearDown(self):
        self.profile = None
        self.genotype = None

    def test_copy(self):
        copy = self.genotype.copy()
        self.assertTrue(self.genotype == copy)
        copy.profile = {}
        self.assertFalse(self.genotype == copy)

    def test_equal_same_profile_same_profilemap(self):
        equal_genotype = EvolveProfile.Genotype(self.profile)
        equal_genotype.profile = self.genotype.profile.copy()
        self.assertTrue(self.genotype == equal_genotype)

    def test_equal_same_profile_different_profilemap(self):
        different_genotype = EvolveProfile.Genotype({})
        different_genotype.profile = self.genotype.profile.copy()
        self.assertFalse(self.genotype == different_genotype)

    def test_equal_different_profile_same_profilemap(self):
        different_genotype = EvolveProfile.Genotype(self.profile)
        self.assertFalse(self.genotype == different_genotype)

    def test_equal_different_profile_different_profilemap(self):
        different_genotype = EvolveProfile.Genotype({})
        self.assertFalse(self.genotype == different_genotype)
        

    def test_get_context_values(self):
        profile = {
            'a': 1,
            'b': 2,
            'c': 3,
            'dict1': {
                'd': 4,
                'e': 5,
                'f': 6,
                'dict2': {
                    'g': 7,
                    'h': 8,
                }
            }
        }
        contexts = [
            ['a', 1],
            ['b', 2],
            ['c', 3],
            ['dict1', 'd', 4],
            ['dict1', 'e', 5],
            ['dict1', 'f', 6],
            ['dict1', 'dict2', 'g', 7],
            ['dict1', 'dict2', 'h', 8],
        ]
        contexts.sort()
        gotcontexts = self.genotype.get_contexts(profile)
        self.assertEqual(contexts, gotcontexts)

    def test_build_dict_from_context(self):
        contexts = [
            ['a', 1],
            ['b', 2],
            ['c', 3],
            ['dict1', 'd', 4],
            ['dict1', 'e', 5],
            ['dict1', 'f', 6],
            ['dict1', 'dict2', 'g', 7],
            ['dict1', 'dict2', 'h', 8],
        ]
        expected_dict = {
            'a': 1,
            'b': 2,
            'c': 3,
            'dict1': {
                'd': 4,
                'e': 5,
                'f': 6,
                'dict2': {
                    'g': 7,
                    'h': 8
                }
            }
        }
        got_dict = self.genotype.build_dict_from_context(contexts)
        self.assertEqual(expected_dict, got_dict)

    def test_add_subdict_no_overwrite(self):
        context_list = ['a', 'b', 'c']
        dct = {
            'a': {
                'some_val': 1776
            },
            'q': 'stuff',
        }
        expected_dct = {
            'a': {
                'some_val': 1776,
                'b': {
                    'c': {
                    }
                }
            },
            'q': 'stuff',
        }
        self.genotype.add_subdicts(context_list, dct)
        self.assertEqual(dct, expected_dct)
        
    def test_add_subdict_empty(self):
        context_list = ['a', 'b', 'c']
        dct = {}
        expected_dct = {
            'a': {
                'b': {
                    'c': {
                    }
                }
            }
        }
        self.genotype.add_subdicts(context_list, dct)
        self.assertEqual(dct, expected_dct)

    def test_mutate(self):
        init_values = set(self._all_the_values(self.genotype.profile))
        self.genotype.mutate()
        new_values = set(self._all_the_values(self.genotype.profile))
        self.assertTrue(len(init_values - new_values) == 1)

    def test_all_the_values(self):
        dct = {
            'a': 1,
            'b': 2,
            'c': 3,
            'newdct': {
                'd': 4,
                'e': 5,
            }
        }
        all_values = set([1, 2, 3, 4, 5])
        got_values = set(self._all_the_values(dct))
        self.assertTrue(len(all_values - got_values) == 0)

    def _all_the_values(self, dct, values=[]):
        values = []
        for key in dct:
            if isinstance(dct[key], dict):
                values.extend(self._all_the_values(dct[key], values))
            else:
                values.append(dct[key])
        return values

    def test_randomize_value_list(self):
        value = ['l', 1, 2, 'a', 'b']
        for i in range(10):
            rval = self.genotype.randomize_value(value)
            self.assertTrue(rval in value)

    def test_randomize_value_min_max(self):
        value = ['r', 0, 50]
        for i in range(10):
            rval = self.genotype.randomize_value(value)
            self.assertTrue(rval >= value[1])
            self.assertTrue(rval <= value[2])

    def test_uniform_crossover(self):
        mate = EvolveProfile.Genotype(self.profile)
        progeny = self.genotype.uniform_crossover(mate)
        progeny = EvolveProfile.Genotype(self.profile, ingenotype=progeny)
        this_context = self.genotype.get_contexts(self.genotype.profile)
        mate_context = mate.get_contexts(mate.profile)
        progeny_context = progeny.get_contexts(progeny.profile)
        for parent in [this_context, mate_context]:
            self.assertEqual(len(progeny_context), len(parent))
        for c in progeny_context:
            self.assertTrue(c in this_context or c in mate_context)

class TestGenotype_Random_Config(unittest.TestCase):

    def setUp(self):
        self.genotype = EvolveProfile.Genotype({})

    def tearDown(self):
        self.genotype = None

    def test_randomize_profile_not_nested_only_min_max_pair(self):
        profile = {
            "minmaxA": ['r', 0, 1],
            "minmaxB": ['r', -50, -40],
            "minmaxC": ['r', 5.0, 10.0],
        }
        randomized_profile = self.genotype.randomize_profile(profile)
        self.check_values(profile, randomized_profile)

    def test_randomize_profile_not_nested_list(self):
        profile = {
            "listA": ['l', 'asdf'],
            "listB": ['l', 'a', 'b', 'c', 'd'],
            "listC": ['l', 'a', 1, 2, 'b'],
        }
        randomized_profile = self.genotype.randomize_profile(profile)
        self.check_values(profile, randomized_profile)

    def test_randomize_profile_not_nested_list_and_min_max_pair(self):
        profile = {
            "minmaxA": ['r', 0, 50],
            "listA": ['l', 1, 2, 3, 4, 5],
            "listB": ['l', 'a', 'b', 'c', 'd'],
            "minmaxB": ['r', -50, 0],
        }
        randomized_profile = self.genotype.randomize_profile(profile)
        self.check_values(profile, randomized_profile)

    def test_randomize_profile_nested_list_and_min_max_pair(self):
        profile = {
            "minmaxA": ['r', 0, 50],
            "listA": ['l', 1, 2, 3, 4, 5],
            "listB": ['l', 'a', 'b', 'c', 'd'],
            "minmaxB": ['r', -50, 0],
            "subDict": {
                "minmaxC": ['r', 5, 10],
                "listC": ['l', 5, 4, 3, 2, 1],
            }
        }
        randomized_profile = self.genotype.randomize_profile(profile)
        self.check_values(profile, randomized_profile)
        self.check_values(profile['subDict'], randomized_profile['subDict'])

    def check_values(self, profile, random_profile):
        for key in random_profile:
            self.assertTrue(key in profile)
            val = random_profile[key]
            if isinstance(random_profile[key], dict):
                pass
            elif 'minmax' in key:
                self.assertTrue(val >= profile[key][1])
                self.assertTrue(val <= profile[key][2])
            else:
                self.assertTrue(val in profile[key])

if __name__ == "__main__":
    unittest.main()
