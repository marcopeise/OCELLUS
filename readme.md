# Bibtext Filter

A simple tool for searching ScienceDirect, Springer, IEEE and ACM API and applying filters on the results. 

**Usage:** `python3 main.py -af args.json`

**Arguments:**
   - `-af, --argsfile` : Name and path of the argument file (args.json)
 
## Features:
- Filter ScienceDirect, Springer, IEEE and ACM by concepts on certain fields
- add custom operands for more advanced queries
- export passed and failed entries


## the args.json file:
Certain arguments must be passed for using this tool. The following is an example of a minimum configuration:
```json
{
    "concepts": [
        ["blockchain", "distributed ledger"], 
        ["market", "trading"]
    ],
    "fields": [
        ["title"],
        ["keyword"]
    ],
    "sources": {
        "springer": true,
        "ieee": true,
        "acm": false,
        "science_direct": false
    }
}
```
The idea is that that one can define 'concepts' and 'fields'. Concepts contain and array of words that are supposed to be thematic synonyms. For example, some papers might use the word blockchain, while others might use distributed ledger in their's. When grouping these words in a concept, this program will treat them as synonyms, meaning a paper can contain either word interchangeably, without affecting the result. The fields used, must be defined as keys in dict.json, in the field_synonyms object.


## the dict.json file:
```json
{
    "field_synonyms": {
        "ieee": {
            "abstract": ["Abstract"],
            "title": ["Document Title"],
            "keyword": ["Author Keywords"]
        },
        "acm": {
            "title": ["title", "booktitle"]
        },
        "science_direct": {
            "title": ["Title"],
            "abstract": ["abs"],
            "keyword": ["key"]
        }
    },
    "api_keys": {
        "springer": "d9f600d5b3bf91e3c***********",
        "ieee": "eyxc5mxv56st2************",
        "science_direct": "69340b3564cc587***********"
    },
    "accepted_fields": {
        "ieee": ["Abstract","Document Title", "Author Keywords"],
        "springer": ["keyword", "title", "abstract"],
        "science_direct": ["abs", "Title", "key"]
    }   
}
```

The dict.json file is used for two reasons, first of all it stores the API keys for all used API's, more importantly though, it is used for normalizing the different field names of the different API's. 

### field_synonym's:
This object is used for nomalizing the names for the same fields, on the different API's. For example, IEEE calls the title "Document Title", while ACM calls it "title" and "booktitle". In order to use all API's without special configuration for each request we use this object. The keys for each field_synonym are the field names used in this tool, while the values are the names used by the API. Currently "abstract", "title", "keyword" are the only fields that can be used safelty without any configuration, because the field_synonyms have been added. 

### accepted_field's:
This object simply contains an array of fields, that is accepted for each API. (A lot more can be added by searching through the API Documentation)
### Resulting Query:
args.json and dict.json will generate the following queries:

#### Springer:
```
(title=distributed ledger OR keywords=distributed ledger OR title=decentralized OR keywords=decentralized)
AND
(title=market OR keywords=market OR title=trading OR keywords=trading)
```
When this query is created, the program check, if Springer has any field_synonyms, but since it doesnt, it uses the given field names to creater the query.

#### IEEE:
```
(Document Title=blockchain OR Author Keywords=blockchain OR Document Title=distributed ledger OR Author Keywords=distributed ledger)
AND
(Document Title=market OR Author Keywords=market OR Document Title=trading OR Author Keywords=trading)
```
With this query, the program checks for field_synonyms again, finds them, and uses the synonyms for the query. 

## Other configurations

### 1. passing operands:
The args.json file has a field called 'operands' which can contain an array of operations that can be added to the search. 

Example:
 ```json
  { "operands": [
        {   
            "field": "year", 
            "operator": "<=", 
            "value":2017
        },
        {   
            "field": "abstract", 
            "operator": "==", 
            "value":"This is a test"
        }
    ]
}
 ```
 
 There are two type of operations that can be performed with this argument, string based operations and integer based operations. 
 
 ##### String based operations:
 
 - used by setting the opperator to "=="
 - value must passed as a string
 When passed the script will check if given field has the exact same value as passed in the value field

##### Interge based operations:
**Supported Operators:** '<', '<=', '>', '>=', '!='
- pass any operator in the operator field
- value must be an integer


### 2. Defining file names:

File names for both output files can be defined via the args.json file. 

```json
{ "settings": {
        "failed_name": "failed_entries.json",
        "passed_name": "passed_entries.bib"
    }
}
```

## Example args.json file:

```json
{
    "concepts": [
        ["blockchain", "smart contract", "distributed ledger", "decentralized"], 
        ["market", "trading"], 
        ["electricity", "energy"]],
    "fields": [
        ["title"],
        ["abstract"],
        ["keyword"]
    ],
    "operands": [
        {   
            "field": "year", 
            "operator": "<=", 
            "value":"2017"
        }
    ],
    "settings": {
        "failed_name": "failed_entries.json",
        "passed_name": "passed_entries.bib"
    }
}
```





















