from collections import defaultdict
import re
import sys

from common.folder_processor import FolderProcessor
from common.io import MyEncoder, read_object, write_object


class Keyword(object):
    def __init__(self, keyword):
        self.keyword = keyword
        self.count = 0
        self.related_keywords_distribution = defaultdict(int)

    def add_related(self, other_keywords):
        for keyword in other_keywords:
            self.related_keywords_distribution[keyword] += 1


def split_keyword(value):
    return re.split("[,;]", value)


def split_keywords(metadata):
    return [
        keyword.strip()
        for keyword in split_keyword(metadata.get("metadata", {}).get("Keywords", ""))
    ]

DATA = {
    "documents_without_keywords": [],
    "keywords_distribution": {},
    "analyzed_documents_count": 0,
}


def process_single_file(path):
    try:
        metadata = read_object(path)
    except:
        return

    document_keywords = split_keywords(metadata)
    document_keywords = [keyword.lower() for keyword in document_keywords if keyword]
    if not document_keywords:
        DATA["documents_without_keywords"].append(path)
    keywords_data = DATA["keywords_distribution"]
    for keyword in document_keywords:
        kd = keywords_data.get(keyword, Keyword(keyword))
        kd.count += 1
        kd.add_related(document_keywords)
        keywords_data[keyword] = kd

    DATA["keywords_distribution"] = keywords_data
    DATA["analyzed_documents_count"] += 1


def keywords_count(data):
    for a, b in sorted(
        data.get("keywords_distribution").items(),
        key=lambda kv: (kv[1]["count"], kv[0]),
    ):
        if b["count"] > 1 and "adb" not in a:
            print(f"{b['count']}, {a}")


def related(data, keyword):
    dico = data["keywords_distribution"][keyword]["related_keywords_distribution"]
    for a, b in sorted(dico.items(), key=lambda kv: (kv[1], kv[0])):
        print(f"{a}, {b}")


def main(folders=None):
    analysis_path = "data/intermediate/describe/keywords_distribution.json"

    try:
        data = read_object(analysis_path)
    except:
        if not folders:
            folders = [
                "data/input/pdf-generic",
                "data/input/technical",
                "data/input/reports",
            ]
        FolderProcessor(
            folders, "*.metadata.json", process_single_file
        ).process_folders()
        write_object(DATA, analysis_path, cls=MyEncoder)
        print("please execute this script once again")
        sys.exit(0)

    keywords_count(data)
    # print('*** keywords related to "china" ***')
    # related("china")
    # print(f"we analyzed {data['analyzed_documents_count']} documents, but {len(data['documents_without_keywords'])} had no keywords")
    print(
        f"word cloud built upon {data['analyzed_documents_count'] - len(data['documents_without_keywords'])} documents"
    )
    print(f"{len(data['keywords_distribution'].keys())} keywords")


if __name__ == "__main__":
    main()
