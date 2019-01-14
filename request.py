from requestSpringer import RequestSpringer
from requestScienceDirect import RequestScieneDirect
from requestIeee import RequestIeee
from fileOps import FileClass
from perm import Permutation
from response import Response
from filterOps import Filter
from pprint import pprint
import sys

class Request:
    def __init__(self, args, operands, passed_name, failed_name):
        self.args = args
        self.operands = operands
        self.passed_name= passed_name
        self.failed_name = failed_name
        self.dict_file_path = "dict.json"
        self.file_handle = FileClass()
        self.data_responses = []
        self.response = Response()
        self.results = []
        # pprint(self.args)

    # Initialize instances of reques classes
    def initialize_request_classes(self):
            self.springer = RequestSpringer(self.args, self.dict_file_path)
            self.science_direct = RequestScieneDirect(self.args, self.dict_file_path)
            self.ieee = RequestIeee(self.args, self.dict_file_path)

    # calls checks methods and run_request if checks pass
    def peform_checks_and_execute(self):
        if self.args["sources"]["springer"] and self.check_fields('springer'):
            self.run_requests("springer")
        if self.args["sources"]["science_direct"] and self.check_fields('science_direct'):
            self.run_requests("science_direct")
        if self.args["sources"]["ieee"] and self.check_fields('ieee'):
            self.run_requests("ieee")

    # remove duplicates controller methid
    def remove_duplicates(self):
        self.response.set_responses(self.data_responses)
        self.response.remove_duplicates()
        self.results = self.response.get_reponses()

    # filter contoller function
    def perform_filter(self):
        self.filter = Filter(self.results, self.args["concepts"], self.args["fields"], self.operands, self.passed_name, self.failed_name)
        self.filter.iterate_entries()
        self.filter.write_res()

    # controller function for field checks
    def check_fields(self, source_name):
        fields = self.merge_synonyms(source_name)
        field_check = self.check_field_validity(fields, source_name)
        if field_check[0]:
            return True
        else:
            print(field_check[1])
            print("unaccepted fields found in concepts!")
            sys.exit()
            return False

    # controller function for different sources
    def run_requests(self, source_name):
        if source_name == "springer":
            self.springer.get_permutations()
            self.springer.iterate_permutation()
            self.springer.clean_entries()
            self.data_responses += self.springer.cleaned_res
        if source_name == "science_direct":
            self.science_direct.get_permutations()
            self.science_direct.iterate_permutation()
            # self.science_direct.clean_entries()
            self.data_responses += self.science_direct.req_res
            # print(len(self.data_responses))
        if source_name == "ieee":
            self.ieee.get_permutations()
            self.ieee.iterate_permutation()
            self.ieee.clean_entries()
            self.data_responses += self.ieee.cleaned_res

    # merges fields with synonyms of data source, e.g. title => booktitle, title
    def merge_synonyms(self, source_name):
        synonyms = self.file_handle.get_synonyms(source_name, self.dict_file_path)
        included_keys = []
        for key in self.args["fields"]:
            if key[0] in synonyms:
                included_keys += synonyms[key[0]]
            else:
                included_keys.append(key[0])
        return included_keys

    # check if field is accepted for given source, e.g. haha123 is not a field that can be queried
    def check_field_validity(self, fields, source_name):
        accepted_fields = self.file_handle.open_json(self.dict_file_path)["accepted_fields"][source_name]
        accepted = True
        rejected = []
        for field in fields:
            if field in accepted_fields:
                continue
            else:
                accepted = False
                rejected.append(field)
        return (accepted, rejected)

