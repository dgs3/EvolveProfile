import subprocess
import os
import json
import tempfile

class PhysicalFitnessCalculator(object):

    def __init__(self, model_dir, profile_path=None):
        self.model_paths = self.get_model_paths(model_dir)
        if profile_path:
            self.profile_path = profile_path
        else:
            self.profile_path = os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                'miracle.config'
            )
        with open(self.profile_path) as f:
            self.profile = json.load(f)
        self.check_call = subprocess.check_call
        self.model_transition = [
            'G1 X0 Y0 Z150 F2500; Transition from one model to the next\n',
            'G92 A0 B0\n',
        ]

    def _create_transition(self, model_path):
        comment = '; Here follows %s\n' % (model_path)
        return [comment] + self.model_transition

    def get_model_paths(self, model_dir):
        models = []
        for model in os.listdir(model_dir):
            ext = os.path.splitext(model)
            if '.stl' == ext[1]:
                models.append(os.path.join(
                    model_dir,
                    model,
                ))
        return models

    def write_out_config(self, the_json):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            f.write(json.dumps(the_json))
            path = f.name
        return path

    def slice_models(self, model_paths, config_paths):
        assert(len(model_paths) == len(config_paths)) 
        with tempfile.NamedTemporaryFile(suffix='.gcode', delete=False) as f:
            allpath = f.name
            for model_path, config_path in zip(model_paths, config_paths):
                info = self._slice(model_path, config_path)
                for code in self._create_transition(model_path):
                    f.write(code)
                with open(info['output_path']) as o:
                    f.write(o.read())
        return allpath

    def _slice(self, model_path, config):
        assert(os.path.exists(model_path))
        with tempfile.NamedTemporaryFile(suffix='.gcode', delete=False) as f:
            output_path = f.name
        total_config = config.copy()
        total_config.update(self.profile)
        config_path = self.write_out_config(total_config)
        call = self.build_call(model_path, output_path, config_path)
        try:
            self.check_call(call)
        except Exception as e:
            print("Make sure MG is in your path bro.")
            raise e
        return {
            'output_path': output_path,
            'config_path': config_path,
        }

    @staticmethod
    def build_call(input_path, output_path, config_path):
        path_to_mg = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'bins',
            'miracle_grue',
        )
        return [path_to_mg, '-c%s' % (config_path), '-o%s' % (output_path), input_path]
