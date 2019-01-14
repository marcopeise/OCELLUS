import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
import json, sys, os
from lxml import html
import requests
from request import Request
from fileOps import FileClass

class Main:
    def __init__(self, args):
        # removes first argument which is not needed
        args.pop(0)
        self.args = args
        self.argument_file = "args.json"
        self.concept = None
        self.field_sets = None
        self.operands = None
        self.passed_name = "passend_entries.bib"
        self.failed_name = "failed_entries.json"
        self.fileOps = FileClass()

    # parses cl args, and calls needed methods for reading data
    # def parse_cl_args(self):
    #     if self.args[0] == "-h" or self.args[0] == "--help" or self.args[0] == "help":
    #         print("Example usage:")
    #         print("python3 script.py")
    #         sys.exit()
    #     else:
    #         self.parse_argument_file()

    # parse argument json file
    def parse_argument_file(self):
        self.argument_file = self.fileOps.open_json(self.argument_file)

    def perform_argument_checks(self):
        self.check_file_arguments()
        self.set_settings()
        self.check_operands()

    # checks if arguments are valid
    def check_file_arguments(self):
        if len(self.argument_file["concepts"]) == 0:
            print("No concepts specified! Please check arguments file!")
        elif len(self.argument_file["fields"]) == 0:
            print("No fields specified! Please check arguments file!")
        else:
            self.concepts = self.argument_file["concepts"]
            self.field_sets = self.argument_file["fields"]
            self.operands = self.check_for_dict_entry("operands", self.argument_file)
            self.settings = self.check_for_dict_entry("settings", self.argument_file)

    # checks if passed operands are valid
    def check_operands(self):
        for op in self.operands:
            if isinstance(op["value"], int):
                # check if operator is supported, for string operations it doesnt matter as one operation is only supported
                if op["operator"] != ">" and op["operator"] != "<" and op["operator"] != "!=" and op["operator"] != "<=" and op["operator"] != ">=":
                    print(
                        "Operator is not supported! Check documentation for more information")
                    print("Operator passed: " + op["operator"])

    def set_settings(self):
        if "failed_name" in self.settings and self.failed_name == "failed_entries.json":
            self.failed_name = self.settings["failed_name"]
        if "passed_name" in self.settings and self.passed_name == "passed_entries.bib":
            self.passed_name = self.settings["passed_name"]
    
    # safe access method for dict, returns emtpy list if key not found
    def check_for_dict_entry(self, key, obj):
        if key in obj:
            return obj[key]
        return []

    def perform_query(self):
        self.request = Request(self.argument_file, self.operands, self.passed_name, self.failed_name)
        self.request.initialize_request_classes()
        self.request.peform_checks_and_execute()
        self.request.remove_duplicates()
        self.request.perform_filter()


if __name__ == "__main__":
    test = Main(sys.argv)
    test.parse_argument_file()
    test.perform_argument_checks()
    test.perform_query()
