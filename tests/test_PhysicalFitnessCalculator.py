import os
import sys
lib_path = os.path.abspath('./')
sys.path.insert(0, lib_path)

import unittest
import json
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

    def test_get_model_paths(self):
        expected_model_paths = []
        for path in os.listdir(self.model_path):
            if '.stl' == os.path.splitext(path)[1]:
                expected_model_paths.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test_models', path))
        got_model_paths = self.pfc.get_model_paths(self.model_path)
        self.assertEqual(len(expected_model_paths), len(got_model_paths))
        for a, b in zip(expected_model_paths, got_model_paths):
            self.assertTrue(os.path.samefile(a, b))

    def test_write_out_config(self):
        expected_json = {
            'a': 1,
            'b': 2,
            'c': 3,
        }
        path = self.pfc.write_out_config(expected_json)
        with open(path) as f:
            got_json = json.load(f)
        self.assertEqual(expected_json, got_json)

    def test_slice_makes_right_call(self):
        self.pfc.check_call = mock.Mock()
        model_path = 'dummy_model.stl'
        config = {
            'a': 1,
            'b': 2,
            'c': 3,
        }
        info = self.pfc._slice(model_path, config)
        with open(info['config_path']) as f:
            got_config = json.load(f)
        with open(os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'EvolveProfile',
            'miracle.config',
        )) as f:
            proper_config_map = json.load(f)
        got_config.update(proper_config_map)
        config.update(proper_config_map)
        self.assertEqual(config, got_config)
        self.assertTrue(os.path.exists(info['output_path']))
        call = self.pfc.build_call(model_path, info['output_path'], info['config_path'])
        self.pfc.check_call.assert_called_once_with(call)

if __name__ == "__main__":
    unittest.main()
