import json
import requests
from typing import Dict, Any
import hashlib
from slugify import slugify


LIMIT = 100000
ES_SERVER_ADDRESS = "http://localhost:9200"
ES_INDEX_NAME_FORMAT = "s_{organization_id}_adb_people_v1"
DEFAULT_INDEX_SETTINGS = {
    "settings": {
        "index": {
            "highlight.max_analyzed_offset": 100000,
            "analysis": {
                "analyzer": {
                    "search_synonyms": {
                        "tokenizer": "whitespace",
                        "filter": ["lowercase", "graph_synonyms"],
                    }
                },
                "filter": {
                    "graph_synonyms": {
                        "type": "synonym_graph",
                        "synonyms_path": "analysis/default-synonyms.txt",
                    }
                },
            },
        }
    },
    "mappings": {
        "properties": {
            "keywords": {
                "type": "nested",
                "properties": {
                    "keyword": {"type": "keyword", "ignore_above": 256},
                    "count": {"type": "float"},
                },
            },
        }
    },
}


def dict_hash(dictionary: Dict[str, Any]) -> str:
    """MD5 hash of a dictionary."""
    dhash = hashlib.md5()
    # We need to sort arguments so {'a': 1, 'b': 2} is
    # the same as {'b': 2, 'a': 1}
    encoded = json.dumps(dictionary, sort_keys=True).encode()
    dhash.update(encoded)
    return dhash.hexdigest()


def index_documents(organization_id, documents):
    index_name = setup_index(organization_id)

    for document in documents:
        index_single_document(index_name, document)


def setup_index(organization_id):
    index_name = ES_INDEX_NAME_FORMAT.format(organization_id=organization_id)
    index_uri = f"{ES_SERVER_ADDRESS}/{index_name}"
    response = requests.put(
        index_uri,
        json=DEFAULT_INDEX_SETTINGS,
        headers={"content-type": "application/json"},
    )
    print(response)
    return index_name


def index_single_document(index_name, document):
    doc_id = document.get("id")
    doc_uri = f"{ES_SERVER_ADDRESS}/{index_name}/_doc/{doc_id}"
    response = requests.put(
        doc_uri, json=document, headers={"content-type": "application/json"}
    )
    print(response)
    return response


def prepare_texts(documents):
    for document in set(documents):
        with open(f"{document}.metadata.json") as fd:
            doc = json.load(fd)
        yield doc["content"]


def shorten(texts):
    for text in texts:
        cut = len(text) - LIMIT
        if cut > 0:
            text[:-cut]
        yield text


def prepare_keywords(keywords):
    for keyword, count in keywords.items():
        yield {"keyword": keyword, "count": count}


def index_authors_documents(index_name):
    with open("data/intermediate/author_documents.json") as fd:
        author_documents = json.load(fd)

    count = 0
    for author, document in author_documents.items():
        es_document = dict(document)
        es_document["id"] = slugify(author)
        es_document["author"] = author
        es_document["texts"] = list(prepare_texts(es_document["documents"]))
        es_document["texts_cut"] = list(shorten(es_document["texts"]))
        es_document["keywords"] = list(prepare_keywords(es_document["keywords"]))
        index_single_document(index_name, es_document)
        count += 1

    print(f"{count} documents indexed so far.")


if __name__ == "__main__":
    index_name = setup_index(1)
    index_authors_documents(index_name)
