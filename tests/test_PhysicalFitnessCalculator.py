import os
import sys
lib_path = os.path.abspath('./')
sys.path.insert(0, lib_path)

import unittest
import json
import tempfile
import mock

import EvolveProfile

class TestPhysicalFitnessCalculator(unittest.TestCase):

    def setUp(self):
        self.model_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'test_models'
        )
        self.pfc = EvolveProfile.PhysicalFitnessCalculator(self.model_path)

    def tearDown(self):
        self.pfc = None

    def test_ascertain_fitness(self):
        self.pfc.check_call = mock.Mock()
        self.pfc.HCI = mock.Mock()
        fitnesses = [range(10, 15), range(0, 10)]
        def side_effect(*args, **kwargs):
            return fitnesses.pop()
        self.pfc.HCI.ask_fitness = mock.Mock(side_effect=side_effect)
        expected_fitness = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        genotypes = [EvolveProfile.Genotype({}) for i in range(15)]
        got_fitness = self.pfc.ascertain_fitness(genotypes)
        self.assertEqual(expected_fitness, got_fitness)
        calls = self.pfc.HCI.ask_fitness.mock_calls
        self.assertTrue(len(calls) == 2)
       
    def test_get_model_paths(self):
        expected_model_paths = []
        for path in os.listdir(self.model_path):
            if '.stl' == os.path.splitext(path)[1]:
                expected_model_paths.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test_models', path))
        got_model_paths = self.pfc.get_model_paths(self.model_path)
        self.assertEqual(len(expected_model_paths), len(got_model_paths))
        for a, b in zip(expected_model_paths, got_model_paths):
            self.assertTrue(os.path.samefile(a, b))

    def test_write_out_profile(self):
        expected_json = {
            'a': 1,
            'b': 2,
            'c': 3,
        }
        path = self.pfc.write_out_profile(expected_json)
        with open(path) as f:
            got_json = json.load(f)
        self.assertEqual(expected_json, got_json)

    def test_get_profiles(self):
        genotypes = [EvolveProfile.Genotype({}) for i in range(10)]
        profiles = [{'a': i} for i in range(10)]
        for g, p in zip(genotypes, profiles):
            g.profile = p
        got_profiles = self.pfc.get_profiles(genotypes)
        self.assertEqual(profiles, got_profiles)

    def test_slice_makes_right_call(self):
        self.pfc.check_call = mock.Mock()
        with tempfile.NamedTemporaryFile(suffix='.stl', delete=False) as f:
            dummy_model = f.name
        model_path = dummy_model
        profile = {
            'a': 1,
            'b': 2,
            'c': 3,
        }
        info = self.pfc._slice(model_path, profile)
        with open(info['profile_path']) as f:
            got_profile = json.load(f)
        with open(os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'EvolveProfile',
            'miracle.config',
        )) as f:
            proper_profile_map = json.load(f)
        got_profile.update(proper_profile_map)
        profile.update(proper_profile_map)
        self.assertEqual(profile, got_profile)
        self.assertTrue(os.path.exists(info['output_path']))
        call = self.pfc.build_call(model_path, info['output_path'], info['profile_path'])
        self.pfc.check_call.assert_called_once_with(call)

if __name__ == "__main__":
    unittest.main()
