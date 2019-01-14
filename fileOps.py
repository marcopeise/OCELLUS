import json, os
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
from pprint import pprint

class FileClass:
    # method for opening json file fom FS
    def open_json(self, path):
        parsed_json = None
        if os.path.exists(path):
            with open(path) as f:
                try:
                    parsed_json = json.load(f)
                except:
                    print("File couldnt be parsed, please check if its valid json")
        else:
            print("File couldn't be found! Please check path: " + path)
        return parsed_json
    
    def write_res(self, passed_entries, passed_name, failed_entries, failed_name):
        db = BibDatabase()
        db.entries = passed_entries
        writer = BibTexWriter()
        writer.indent = '    '
        writer.comma_first = False
        with open("results/" + passed_name, 'w') as bibfile:
            bibfile.write(writer.write(db))
        with open("results/" + failed_name, 'w') as f:
            json.dump(failed_entries, f, indent=4)
        

        print("Writing data to filesystem!")
        print("  -successful results can be found in: results/" + passed_name)
        print("  -failed results can be found in: results/" + failed_name)

    # returns dict of synonyms for given source
    def get_synonyms(self, source_name, dict_file_path):
        json_file = self.open_json(dict_file_path)
        if source_name in json_file["field_synonyms"]:
            return json_file["field_synonyms"][source_name]
        else:
            return {}
