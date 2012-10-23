from __future__ import absolute_import

import random

class Genotype(object):

    def __init__(self, profilemap, ingenotype=None):
        self.profilemap = profilemap
        self.profile = self.randomize_profile(self.profilemap) if not ingenotype else ingenotype

    def __eq__(self, other):
        return self.profile == other.profile and self.profilemap == other.profilemap

    def copy(self):
        profile_copy = self.profile.copy()
        profilemap_copy = self.profilemap.copy()
        return Genotype(profilemap_copy, ingenotype=profile_copy)

    def randomize_profile(self, profilemap):
        """
        Randomizes a profile using the profilemap passed in

        @param dict profilemap: Map of the profile the genotype uses
        @return dict: A randomized profile with the same structure as the profilemap
        """
        rand_prof = {}
        return self._recursize_randomize(profilemap, rand_prof)

    def _recursize_randomize(self, profilemap, rand_prof):
        """
        Recursive funtion to randomize a profile using a profile map

        @param dict profilemap: Profilemap used to randomize a profile
        @param dict rand_prof: The random profile being created
        @return dict: The randomized profile
        """
        for key in profilemap:
            if isinstance(profilemap[key], dict):
                rand_prof[key] = self._recursize_randomize(profilemap[key], {})
            else:
                rand_prof[key] = self.randomize_value(profilemap[key])
        return rand_prof

    def randomize_value(self, value):
        """
        The random values created are based on entries in self.profilemap.
        For more on these entries, read the README.md file in the root
        of this repo

        @param list value: Value to randomize
        @return value: Randomized value
        """
        rval = None
        if value[0] == 'r':
            minimum = value[1]
            maximum = value[2]
            if isinstance(minimum, int):
                rval = random.randint(minimum, maximum)
            elif isinstance(minimum, float):
                rval = random.uniform(minimum, maximum)
        elif value[0] == 'l':
            rval = random.choice(value[1:])
        return rval

    def get_contexts(self, profile, context=[]):
        """
        Given a profile, gets a list of its contexts.  A context list
        is a listing of all submaps required to reach a given entry, and 
        the key that leads to the final value.

        @param dict profile: The profile we want to get a context listing of
        @param list context: The listing of contexts
        @return list: List of contexts for each entry for this profile
        """
        list_of_context = []
        for key in profile:
            if isinstance(profile[key], dict):
                list_of_context.extend(self.get_contexts(profile[key], context+[key]))
            else:
                list_of_context.append(context+[key, profile[key]])
        list_of_context.sort()
        return list_of_context
            
    def mutate(self):
        """
        Mutates one random value in this profile
        """
        contexts = self.get_contexts(self.profile)
        choice = random.choice(contexts)
        choice.reverse()
        mut_prof = self.profile
        mut_profmap = self.profilemap
        while len(choice) > 2:
            next_context = choice.pop()
            mut_prof = mut_prof[next_context]
            mut_profmap = mut_profmap[next_context]
        final_context = choice.pop()
        old_val = mut_prof[final_context]
        muted_val = self.randomize_value(mut_profmap[final_context])
        while old_val == muted_val:
            muted_val = self.randomize_value(mut_profmap[final_context])
        mut_prof[final_context] = muted_val

    def uniform_crossover(self, mate):
        """
        Using another mate, executes a uniform crossover, where each loci 
        in the genome has a 50% chance of being passed on to its progeny.
        We do this by creating a context list from the python dict, and
        crossing that over.

        @param Genotype mate: The other mate for this parent
        @return dict: The genome created
        """
        contexts = self.get_contexts(self.profile)
        mate_contexts = mate.get_contexts(mate.profile)
        new_contexts = []
        for context, mate_context in zip(contexts, mate_contexts):
            if random.uniform(0, 1) > .5:
                new_context = context
            else:
                new_context = mate_context
            new_contexts.append(new_context)
        return self.build_dict_from_context(new_contexts)

    def add_subdicts(self, subdict_list, dct):
        """
        Given a list of subdicts, adds those subdicts to a dictionary

        @param list subdict_list: List of subdicts to add
        @param dict dct: Dict to add subdicts to
        """
        if len(subdict_list) == 0:
            return
        else:
            subdict = subdict_list[0]
            del subdict_list[0]
            if not dct.get(subdict, None):
                dct[subdict] = {}
            self.add_subdicts(subdict_list, dct[subdict])

    def build_dict_from_context(self, contexts):
        """
        Given a list of contexts, creates a dictionary

        @param list contexts: List of contexts
        @return dict: Dictionary built from above contexts
        """
        dct = {}
        heirarchy = {}
        for context in contexts:
            self.add_subdicts(context[:-2][:], dct)
            subdct = dct
            while len(context) > 2:
                subdct = subdct[context[0]]
                del context[0]
            subdct[context[0]] = context[1]
        return dct
