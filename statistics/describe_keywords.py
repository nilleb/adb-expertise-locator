from collections import defaultdict
import json
import glob
import re
import sys

from json import JSONEncoder


class Keyword(object):
    def __init__(self, keyword):
        self.keyword = keyword
        self.count = 0
        self.related_keywords_distribution = defaultdict(int)

    def add_related(self, other_keywords):
        for keyword in other_keywords:
            self.related_keywords_distribution[keyword] += 1


def split(value):
    return re.split("[,;]", value)


class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def analysis(folders):
    documents_without_keywords = []
    keywords_data = {}
    count = 0
    for folder in folders:
        paths = glob.glob(f"{folder}/*.metadata.json")
        print(f"{folder}, {len(paths)} paths")
        for path in paths:
            count += 1
            with open(path) as fd:
                metadata = json.load(fd)
                document_keywords = [
                    keyword.strip() for keyword in split(metadata.get("Keywords", ""))
                ]
                document_keywords = [
                    keyword.lower() for keyword in document_keywords if keyword
                ]
                if not document_keywords:
                    documents_without_keywords.append(path)
                for keyword in document_keywords:
                    kd = keywords_data.get(keyword, Keyword(keyword))
                    kd.count += 1
                    kd.add_related(document_keywords)
                    keywords_data[keyword] = kd

    data = {}
    data["documents_without_keywords"] = documents_without_keywords
    data["keywords_distribution"] = keywords_data
    data["analyzed_documents_count"] = count
    return data


analysis_path = "keywords_distribution.json"

try:
    with open(analysis_path) as fd:
        data = json.load(fd)
except:
    folders = ["data/input/pdf-generic", "data/input/technical", "data/input/reports"]
    data = analysis(folders)
    with open(analysis_path, "w") as fd:
        json.dump(data, fd, cls=MyEncoder)
    print("please execute this script once again")
    sys.exit(0)


def keywords_count():
    for a, b in sorted(
        data.get("keywords_distribution").items(),
        key=lambda kv: (kv[1]["count"], kv[0]),
    ):
        if b["count"] > 1 and "adb" not in a:
            print(f"{b['count']}, {a}")


def related(keyword):
    dico = data["keywords_distribution"][keyword]["related_keywords_distribution"]
    for a, b in sorted(dico.items(), key=lambda kv: (kv[1], kv[0])):
        print(f"{a}, {b}")


keywords_count()
# print('*** keywords related to "china" ***')
# related("china")
# print(f"we analyzed {data['analyzed_documents_count']} documents, but {len(data['documents_without_keywords'])} had no keywords")
print(
    f"word cloud built upon {data['analyzed_documents_count'] - len(data['documents_without_keywords'])} documents"
)
