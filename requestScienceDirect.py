from fileOps import FileClass
from perm import Permutation
from pprint import pprint
from lxml import html
import copy
import json
import requests
import time
import sys

class RequestScieneDirect:
    def __init__(self, search_args, dict_file):
        self.search_args = search_args
        self.source_name = "science_direct"
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

    def iterate_permutation(self):
        for perm in self.permutations:
            url = self.build_request_url(perm)
            self.make_request(url)
        pprint(self.req_res)

    def build_request_url(self, query_fields):
        req_url = "https://api.elsevier.com/content/search/sciencedirect?httpAccept=application/json&count=100&query="
        counter = 0
        for key, value in query_fields.items():
            if counter < len(query_fields) - 1:
                req_url += key + "(" + value + ")+and+"
            else:
                 req_url += key + "(" + value + ")&apiKey=" + self.api_key
            counter += 1
        return req_url

    def make_request(self, url, offset=""):
        time.sleep(1)
        print(url + offset) 
        r = requests.get(url + offset).json()
        self.req_res += r['search-results']['entry']
        if int(r['search-results']['opensearch:startIndex']) + int(r['search-results']['opensearch:itemsPerPage']) < int(r['search-results']['opensearch:totalResults']):
            offs = str(int(r['search-results']['opensearch:startIndex']) + int(r['search-results']['opensearch:itemsPerPage']))
            self.make_request(url, "&start=" + offs)

# "https://api.elsevier.com/content/search/sciencedirect?query=abs(bitcoin)+and+title(energy)+and+key(trading)&apiKey=69340b3564cc5870a7f340f220472da6&httpAccept=application/json&count=100"


# "https://api.elsevier.com/content/search/scidir?query=abs(bitcoin)+and+title(energy)+and+key(trading)&start=0&count=25&apiKey=69340b3564cc5870a7f340f220472da6"
# "https://api.elsevier.com/content/metadata/article?query=abs(bitcoin)+and+title(energy)+and+key(trading)&start=0&count=25&apiKey=69340b3564cc5870a7f340f220472da6"
