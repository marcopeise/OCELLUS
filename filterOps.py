from fileOps import FileClass
from pprint import pprint

class Filter:
    def __init__(self, results, concepts, fields, operands, passed_name, failed_name):
        self.fileOps = FileClass()
        self.results = results
        self.concepts = concepts
        self.field_sets = fields
        self.operands = operands
        self.passed_entries = []
        self.failed_entries = []
        self.passed_name = passed_name
        self.failed_name = failed_name

    def iterate_entries(self):
        print("\n # Performing filters and argument checks #")
        for entry in self.results:
            res_concepts = self.iterate_arguments(entry)
            res_operands = self.execute_operands(entry)
            if (self.eval_res(res_concepts) and self.eval_res(res_operands)) is not True:
                self.explain_rejection(res_concepts, res_operands, entry)
            else:
                self.passed_entries.append(entry)
        print("  -Total entries: " + str(len(self.passed_entries) + len(self.failed_entries)))
        print("  -Final passed entries: " + str(len(self.passed_entries)))
        print("  -Failed entries: " + str(len(self.failed_entries)))
        self.fileOps.write_res(self.passed_entries, self.passed_name, self.failed_entries, self.failed_name)

    # loop thats waaaayyyyyyy to deep, though it should stay somewhat around O(n)
    def iterate_arguments(self, bib_entry):
        concepts_checked = [False]*(len(self.concepts))
        for i in range(len(self.concepts)):
            for field_set in self.field_sets:
                if concepts_checked[i]:
                        break
                for field in field_set:
                    if concepts_checked[i]:
                        break
                    for concept_entry in self.concepts[i]:
                        if self.check_argument(field, concept_entry, bib_entry):
                            concepts_checked[i] = True
                            break
                        else:
                            continue
        return concepts_checked

    # logic for concept checks
    def check_argument(self, field, concept_entry, bib_entry):
        if field in bib_entry and concept_entry.lower() in bib_entry[field].lower():
            return True
        return False

    # function for executing and checking passed operands on each bib_entry
    def execute_operands(self, bib_entry):
        # dictionary for string operators which include the functionality as a lambda function
        ops = {">": (lambda x, y: x > y), "<": (lambda x, y: x < y), ">=": (
            lambda x, y: x >= y), "<=": (lambda x, y: x <= y), "!=": (lambda x, y: x != y)}
        res = [False]*(len(self.operands))
        for i in range(len(self.operands)):
            # since there is only one string operation no operation dictionary needed
            if self.operands[i]['operator'] == "==":
                if self.operands[i]['field'] in bib_entry:
                    res[i] = self.operands[i]['value'] == bib_entry[self.operands[i]['field']]
            else:
                if self.operands[i]['field'] in bib_entry:
                    res[i] = ops[self.operands[i]['operator']](
                        int(bib_entry[self.operands[i]['field']]), self.operands[i]['value'])
        return res

    # checks if all checks have passed aka wif we have a match
    def eval_res(self, res):
        if False not in res:
            return True
        return False

    # adds array of concept or operation to dict if they failed during checks
    def explain_rejection(self, res_concepts, res_operands, bib_entry):
        obj = {'name': bib_entry["doi"],
               'failed_concepts': [], 'failed_operands': []}
        for i in range(len(res_concepts)):
            if res_concepts[i] is not True:
                obj['failed_concepts'].append(self.concepts[i])
        for i in range(len(res_operands)):
            if res_operands[i] is not True:
                 obj['failed_operands'].append(self.operands[i])
        self.failed_entries.append(obj)

    def write_res(self):
        self.fileOps.write_res(self.passed_entries, self.passed_name, self.failed_entries, self.failed_name)
