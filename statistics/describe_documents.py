import json
import sys
import glob
from json import JSONEncoder

# Title <class 'str'> 502
# content <class 'str'> 536
# Author <class 'str'> 515
# CreationDate <class 'str'> 535
# Creator <class 'str'> 519
# Keywords <class 'str'> 442
# ModDate <class 'str'> 533
# Producer <class 'str'> 530

def analysis(folders):
    count = 0
    complete_documents = 0
    text_but_no_keywords = 0
    at_least_content = 0

    documents = {}

    for folder in folders:
        paths = glob.glob(f"{folder}/*.metadata.json")
        print(f"{folder}, {len(paths)} paths")
        for path in paths:
            count += 1
            with open(path) as fd:
                metadata = json.load(fd)
                title = metadata.get('Title')
                author = metadata.get('Author')
                content = metadata.get('content')
                keywords = metadata.get('Keywords')
                documents[path] = {
                    'has_title': bool(title),
                    'has_author': bool(author),
                    'has_content': bool(content),
                    'has_keywords': bool(keywords),
                }
                if title and author and content and metadata and keywords:
                    complete_documents += 1
                if content and not metadata:
                    text_but_no_keywords += 1
                if content:
                    at_least_content += 1
    data = {}
    data["complete_documents"] = complete_documents
    data["analyzed_documents_count"] = count
    data["text_but_no_keywords"] = text_but_no_keywords
    data["at_least_content"] = at_least_content
    data['documents'] = documents
    return data

class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

analysis_path = "complete_documents.json"

try:
    with open(analysis_path) as fd:
        data = json.load(fd)
except:
    folders = ["../data/input/pdf-generic", "../data/input/technical", "../data/input/reports"]
    data = analysis(folders)
    with open(analysis_path, "w") as fd:
        json.dump(data, fd, cls=MyEncoder)

print(data)
