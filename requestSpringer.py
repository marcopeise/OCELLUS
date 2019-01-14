from fileOps import FileClass
from perm import Permutation
from pprint import pprint
from lxml import html
import copy
import json
import requests
import time
import sys

class RequestSpringer:
    def __init__(self, search_args, dict_file):
        self.search_args = search_args
        self.source_name = "springer"
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
        print("________________________")
        print("##    Springer:       ##")
        print("________________________\n")
        print("# Permutations #")

        # prints list sorted by abstract if abstract is included!
        if "abstract" in self.permutations[0]:
            pprint(sorted(self.permutations, key=lambda i: i['abstract']))
        else:
            pprint(self.permutations)

        print("\n  Found " + str(len(self.permutations)) + " permutations!")

    # iterates all permutations, builds and makes requests
    def iterate_permutation(self):
        print("\n# Requesting Data #")
        for perm in self.permutations:
            url = self.build_request_url(perm)
            self.make_request(url)

    # make request and handles a query that results in more then 50 entries (api limit) recursivly
    def make_request(self, url, offset=""):
        time.sleep(1)
        print("  Calling: " + url + offset) 
        r = requests.get(url + offset).json()
        self.req_res += r['records']
        if int(r['result'][0]['start']) + int(r['result'][0]['recordsDisplayed']) < int(r['result'][0]['total']):
            offs = str(int(r['result'][0]['start']) + int(r['result'][0]['recordsDisplayed']))
            self.make_request(url, "&s=" + offs)

    # build request url with passed field arguments in accepted format
    def build_request_url(self, query_fields):
        req_url = "http://api.springernature.com/metadata/v1/json?p=50&q=("
        counter = 0
        if "abstract" in query_fields:
            query_fields.pop("abstract")
        for key, value in query_fields.items():
            if counter < len(query_fields) - 1:
                req_url += key + ":'" + value + "' AND "
            else:
                 req_url += key + ":'" + value + "')&api_key=" + self.api_key
            counter += 1
        return req_url

    # cleans and converts data for writing to bibtex file
    def clean_entries(self):
        print("\n# Getting keywords and formating data #")
        for i in range(len(self.req_res)):
            sys.stdout.write("\r  {0}".format(str(i) + "/" + str(len(self.req_res)) + " complete"))
            obj = {}
            # creates id based on name, year and 8 char hash value generated from the title
            obj['ID'] = self.req_res[i]['creators'][0]["creator"].replace(', ', '_') + "_" + self.req_res[i]["publicationDate"].split("-")[0] + str(abs(hash(self.req_res[i]['title'])))[:8]
            obj['ENTRYTYPE'] = self.req_res[i]["contentType"]
            obj["year"] = self.req_res[i]["publicationDate"].split("-")[0]
            obj['url'] = self.req_res[i]["url"][0]["value"]
            obj['author'] = self.build_creators(self.req_res[i]["creators"])
            del self.req_res[i]['url']
            del self.req_res[i]['creators']
            for key, value in self.req_res[i].items():
                if value:
                    obj[key] = self.req_res[i][key]

            if "keyword" not in self.req_res[i]:
                obj["keywords"] = self.get_missing_field(obj['url'], "keywords")
            #removes "abstract from the beginning of every abstract"
            obj['abstract'] = obj['abstract'][8:]
            self.cleaned_res.append(obj)
    
    # brings creators in format needed for bibtex file
    def build_creators(self, creators):
        creators_length = len(creators)
        res = ""
        for idx, val in enumerate(creators):
            if idx < creators_length - 1:
                res += val["creator"] + " and "
            else:
                res += val["creator"]
        return res

    # build url for given data and calls request and parsing function
    def get_missing_field(self, url, field):
        url = "https://link.springer.com/" + url.split("http://dx.doi.org/")[1]
        time.sleep(0.5)
        res = self.make_field_request(url)
        return self.parse_response(res, field)

    # make http request to given link and returns data as xpath compatible object
    def make_field_request(self, url):
        try:
            page = requests.get(url)
            return html.fromstring(page.content)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print(e)
            sys.exit(1)

    # parse keywords from passed response object
    def parse_response(self, response, field):
        # simple test if abstract, keywords and doi exist on the crawled HTML side ?
        keywordsExists = response.xpath('//div[@class="KeywordGroup"]/span[@class="Keyword"]/text()')[0]
        # .extract_first(default='Keywords not-found')

        # ==================================================
        # XPATH for abstract #1
        # ==================================================
        # because of other HTML structure, some entries need other xpaths
        if field == "keywords":
            finalkeywords = ""
            if ("Keywords not-found" in keywordsExists):
                keywordgroupexists = response.xpath('//div[@id="Keywords"]/ul/li[@class="c-keywords__item"]/text()')[0]
                if ("Keywords not-found" not in keywordgroupexists):
                    keywordgroup = response.xpath('//div[@id="Keywords"]/ul/li[@class="c-keywords__item"]/text()')
                    for keyword in keywordgroup:
                        finalkeywords = finalkeywords.rstrip() + ", " + keyword.rstrip()
                else:
                    finalkeywords = keywordgroupexists
            else:
                keywordgroup = response.xpath('//div[@class="KeywordGroup"]/span[@class="Keyword"]/text()')
                for keyword in keywordgroup:
                    finalkeywords = finalkeywords.rstrip() + ", " + keyword.rstrip()
            return finalkeywords

