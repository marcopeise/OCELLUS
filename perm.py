from itertools import permutations
from pprint import pprint
from fileOps import FileClass
import copy
from collections import deque
from collections import deque

class Permutation:
    def __init__(self, args, source_name, dict_file):
        self.args = args
        self.perm_dict_abstract = self.create_dict()
        self.file_handle = FileClass()
        self.dict_file_path = dict_file
        self.source_name = source_name
        self.synonyms = self.file_handle.get_synonyms(self.source_name, dict_file)

    def create_dict(self):
        abstract_dict = {}
        for keys in self.args["fields"]:
            for key in keys:
                abstract_dict[key] = None
        return abstract_dict
        
    
    def create_query_object_templates(self):
        query_lists = self.build_fields_lists()
        concept_perms = self.create_concept_groupings()
      
        return self.build_queries_from_template(query_lists, concept_perms)

    # creates concept groupings, e.g. returns [['smart contract', 'energy', 'trading'], ['blockchain', 'energy', 'trading']] if blockchain and smart conctract are concept synonyms
    def create_concept_groupings(self):
        r = [[]]
        for x in self.args["concepts"]:
            t = []
            for y in x:
                    for i in r:
                        t.append(i+[y])
            r = t
        return r

    # builds array of possible fields combinations, e.g. returns: [[abstract, title, keywords], [abstract, booktitle, keywords]] if title and booktitle are synonyms
    def build_fields_lists(self):
        fields = self.collect_fields_from_dict()
        r = [[]]
        for x in fields:
            t = []
            for y in x:
                    for i in r:
                        t.append(i+[y])
            r = t
        print(r)
        return self.build_fields_permutations(r)

    # builds permutations of all submitted fields and return list of tupels
    def build_fields_permutations(self, query_objects):
        result = []
        for element in query_objects:
            result.append(list(permutations(element)))
        # flatten nested array of tupels
        return [item for sublist in result for item in sublist]

    def collect_fields_from_dict(self):
        res = []
        for field in self.args["fields"]:
            if field[0] in self.synonyms:
                res.append(self.synonyms[field[0]])
            else:
                res.append([field[0]])
        return res


    def build_queries_from_template(self, query_lists, concept_perms):
        final_res = []
        for concept in concept_perms:
            for perm in query_lists:
                obj = {}
                for idx, val in enumerate(perm):
                    obj[val] = concept[idx]
                final_res.append(obj)
        return final_res
