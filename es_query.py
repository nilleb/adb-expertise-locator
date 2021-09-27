import sys
from elasticsearch import Elasticsearch


def compose_query(query_string):
    return {
        "_source": {"includes": ["author", "keywords.keyword", "keywords.count"]},
        "query": {
            "bool": {
                "should": [
                    {"fuzzy": {"author": {"value": query_string}}},
                    {
                        "match": {
                            "texts": {
                                "query": query_string,
                                "analyzer": "search_synonyms",
                            }
                        }
                    },
                    {
                        "nested": {
                            "path": "keywords",
                            "score_mode": "sum",
                            "query": {
                                "function_score": {
                                    "query": {
                                        "match": {"keywords.keyword": query_string}
                                    },
                                    "field_value_factor": {"field": "keywords.count"},
                                }
                            },
                        }
                    },
                ],
                "minimum_should_match": 1,
            }
        },
        "highlight": {
            "require_field_match": False,
            "max_analyzed_offset": 10000,
            "fields": {"texts_cut": {"pre_tags": "<strong>", "post_tags": "</strong>"}},
        },
        "suggest": {
            "text": query_string,
            "suggest-1": {"term": {"field": "author"}},
            "suggest-2": {"term": {"field": "keywords.keyword"}},
        },
    }


es = Elasticsearch()

try:
    query_string = sys.argv[1]
except:
    print(f'Usage: {sys.argv[0]} "terms to search for"')
    exit()

body = compose_query(query_string)
res = es.search(
    index="s_1_adb_people_v1",
    **body,
)

print("Got %d Hits" % res["hits"]["total"]["value"])
suggestions = set()
for suggestion in res["suggest"]["suggest-1"] + res["suggest"]["suggest-2"]:
    for opt in suggestion["options"]:
        suggestions.add(opt.get('text'))
if suggestions:
    print(f"maybe you meant '{' '.join(suggestions)}?'")
for hit in res["hits"]["hits"]:
    print(f'- {hit["_source"]["author"]} ({hit["_score"]})')
    print(f"  > {hit.get('highlight', {}).get('texts_cut')}")
    print()
