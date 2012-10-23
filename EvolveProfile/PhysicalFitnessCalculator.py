import subprocess
import os

class PhysicalFitnessChecker(object)

    def __init__(self, model_dir):
        self.model_paths = self.get_model_paths(model_dir)
        self.check_call = subprocess.check_call

    def get_model_paths(self, model_dir):
        models = []
        for model in model_dir:
            models.append(os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                model,
            )
        return models

    def ascertain_fitness(self, population):
        

    def slice(self, model, config, 
