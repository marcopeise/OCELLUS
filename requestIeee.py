from fileOps import FileClass
from perm import Permutation
from pprint import pprint
from lxml import html
import copy
import json
import requests
import time
import sys

class RequestIeee:
    def __init__(self, search_args, dict_file):
        self.search_args = search_args
        self.source_name = "ieee"
        self.perm = Permutation(search_args, self.source_name, dict_file)
        self.file_handle = FileClass()
        self.dict_file_path = dict_file
        self.api_key = self.get_api_key()
        self.req_res = []
        self.cleaned_res = []

    def get_api_key(self):
        return self.file_handle.open_json(self.dict_file_path)["api_keys"][self.source_name]

    def get_permutations(self):
        self.permutations = self.perm.create_query_object_templates()
        print("\n________________________")
        print("##       IEEE:       ##")
        print("________________________\n")
        print("# Permutations #")
        pprint(self.permutations)
        print("\n  Found " + str(len(self.permutations)) + " permutations!")

    def iterate_permutation(self):
        print("\n# Requesting Data #")
        for perm in self.permutations:
            url = self.build_request_url(perm)
            self.make_request(url)

    # build request url with passed field arguments in accepted format
    def build_request_url(self, query_fields):
        req_url = "http://ieeexploreapi.ieee.org/api/v1/search/articles?max_records=200&querytext=("
        counter = 0
        for key, value in query_fields.items():
            if counter < len(query_fields) - 1:
                req_url += "(\"" + key + "\":" + value + ") AND "
            else:
                 req_url += "(\"" + key + "\":" + value + "))&apikey=" + self.api_key
            counter += 1
        return req_url

    # make request and handles a query that results in more then 50 entries (api limit) recursivly
    def make_request(self, url, offset=0):
        time.sleep(0.5)
        print("  Calling: " + url + "&start_record=" + str(offset))
        r = requests.get(url + "&start_record=" + str(offset)).json()
        self.req_res += r['articles']
        if r['total_records'] > (len(r['articles']) + offset):
            self.make_request(url, offset + 200)

    def clean_entries(self):
        print("# Formating Data #")
        for i in range(len(self.req_res)):
            obj = {}
            # creates id based on name, year and 8 char hash value generated from the title
            obj['ID'] = self.req_res[i]['authors']['authors'][0]["full_name"].replace(' ', '_') + "_" + str(self.req_res[i]["publication_year"]) + "_" + str(abs(hash(self.req_res[i]['title'])))[:8]
            obj['ENTRYTYPE'] = self.req_res[i]["content_type"].lower().replace(" & ", "").replace(" ", "")
            obj["year"] = str(self.req_res[i]["publication_year"])
            obj['url'] = self.req_res[i]["pdf_url"]
            obj['author'] = self.build_creators(self.req_res[i]["authors"]["authors"])
            obj['keywords'] = ", ".join(self.req_res[i]["index_terms"]["author_terms"]["terms"])
            del self.req_res[i]['pdf_url']
            del self.req_res[i]['authors']
            del self.req_res[i]["index_terms"]
            del self.req_res[i]["publication_year"]
            for key, value in self.req_res[i].items():
                if value:
                    obj[key] = str(self.req_res[i][key])
            self.cleaned_res.append(obj)

    #etwas doof wenn mehr als 2 namen stehen, bspw. François de Chezelles
    def build_creators(self, creators):
        creators_length = len(creators)
        res = ""
        for i, val in enumerate(creators):
            sub_res = ""
            if i < creators_length - 1:
                for idx, sub_name in enumerate(list(reversed(val["full_name"].split()))):
                    if idx < len(val["full_name"].split()) - 1:
                        sub_res += sub_name + ", "
                    else:
                        sub_res += sub_name + " and "
            else:
                for idx, sub_name in enumerate(val["full_name"].split()):
                    if idx < len(val["full_name"].split()) - 1:
                        sub_res += sub_name + ", "
                    else:
                        sub_res += sub_name
            res += sub_res
        return res

