import sys
from backends.es import search as es_search


try:
    query_string = sys.argv[1]
except:
    print(f'Usage: {sys.argv[0]} "terms to search for"')
    exit()

res = es_search(query_string)


print("Got %d Hits" % res["hits"]["total"]["value"])
suggestions = set()
for suggestion in res["suggest"]["suggest-1"] + res["suggest"]["suggest-2"]:
    for opt in suggestion["options"]:
        suggestions.add(opt.get("text"))
if suggestions:
    print(f"maybe you meant '{' '.join(suggestions)}?'")
for hit in res["hits"]["hits"]:
    print(f'- {hit["_source"]["author"]} ({hit["_score"]})')
    print(f"  > {hit.get('highlight', {}).get('texts_cut')}")
    print()
