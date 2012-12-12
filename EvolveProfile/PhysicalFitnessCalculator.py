"""
The physical fitness calculator
"""


from ___future___ import unicode_literals, print_function
import json
import os
import subprocess
import tempfile

import EvolveProfile

class PhysicalFitnessCalculator(object):

    def __init__(self, model_dir, profile_path=None):
        self.model_paths = self.get_model_paths(model_dir)
        if profile_path:
            self.master_profile_path = profile_path
        else:
            self.master_profile_path = os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                'miracle.config'
            )
        with open(self.master_profile_path) as f:
            self.master_profile = json.load(f)
        self.check_call = subprocess.check_call
        self.model_transition = [
            'G1 X0 Y0 Z150 F2500; Transition from one model to the next\n',
            'G92 A0 B0\n',
        ]

    def copy_genotypes(self, genotypes):
        """
        Copies a set of genotypes
        """
        copys = []
        for genotype in genotypes:
            copys.append(genotype.copy())
        return copys

    def ascertain_fitness(self, genotypes):
        """
        Gets the fitnesses for a set of genotypes
        """
        num_models = len(self.model_paths)
        copy_genotypes = self.copy_genotypes(genotypes)
        fitnesses = []
        path_to_print_exe = '/examples/print_gcode_file.py'
        while len(copy_genotypes) > 0:
            to_print = copy_genotypes[:num_models]
            profiles = self.get_profiles(to_print)
            all_path = self.slice_models(self.model_paths[:len(to_print)], profiles)
            self.check_call([
                'python', 
                os.path.join(EvolveProfile.s3g_path, path_to_print_exe),
                '-f %s' % (all_path)
            ])
            fitness = self.HCI.ask_fitness(num_models)
            fitnesses.extend(fitness)
            copy_genotypes = copy_genotypes[num_models:]
        return fitnesses

    def get_profiles(self, genotypes):
        profiles = [genotype.profile for genotype in genotypes]
        return profiles
            
    def _create_transition(self, model_path):
        comment = '; Here follows %s\n' % (model_path)
        return [comment] + self.model_transition

    def get_model_paths(self, model_dir):
        """
        Retrieves all stl models in a specific directory

        @param str model_dir: Directory to look in
        @return list models: List of paths to all stl models
        """
        models = []
        for model in os.listdir(model_dir):
            ext = os.path.splitext(model)
            if '.stl' == ext[1]:
                models.append(os.path.join(
                    model_dir,
                    model,
                ))
        return models

    def write_out_profile(self, the_json):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            f.write(json.dumps(the_json))
            path = f.name
        return path

    def slice_models(self, model_paths, profiles):
        assert(len(model_paths) == len(profiles)) 
        with tempfile.NamedTemporaryFile(suffix='.gcode', delete=False) as f:
            allpath = f.name
            for model_path, profile in zip(model_paths, profiles):
                info = self._slice(model_path, profile)
                for code in self._create_transition(model_path):
                    f.write(code)
                with open(info['output_path']) as o:
                    f.write(o.read())
        return allpath

    def _slice(self, model_path, profile):
        assert(os.path.exists(model_path))
        with tempfile.NamedTemporaryFile(suffix='.gcode', delete=False) as f:
            output_path = f.name
        total_profile = self.master_profile.copy()
        total_profile.update(profile)
        profile_path = self.write_out_profile(total_profile)
        call = self.build_call(model_path, output_path, profile_path)
        try:
            self.check_call(call)
        except Exception as e:
            print("Make sure MG is in your path bro.")
            raise e
        return {
            'output_path': output_path,
            'profile_path': profile_path,
        }

    @staticmethod
    def build_call(input_path, output_path, profile_path):
        path_to_mg = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'bins',
            'miracle_grue',
        )
        return [path_to_mg, '-c%s' % (profile_path), '-o%s' % (output_path), input_path]
