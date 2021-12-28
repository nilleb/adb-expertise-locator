import logging
import json
from slugify import slugify
import sys

from configuration import LIMIT
from backends.es import create_indexer

logging.basicConfig(level=logging.INFO)


DOCUMENTS_SOURCE_FORMAT = "data/intermediate/{what}_documents.json"

idx = create_indexer()


def shorten(texts):
    for text in texts:
        cut = len(text) - LIMIT
        if cut > 0:
            text[:-cut]
        yield text


def prepare_texts(documents):
    for document in set(documents):
        with open(f"data/input/{document}.metadata.json") as fd:
            doc = json.load(fd)
        yield doc["content"]


def prepare_keywords(keywords):
    for keyword, count in keywords.items():
        yield {"keyword": keyword, "count": count}


def index_authors_documents(what):
    idx.setup_index()

    with open(DOCUMENTS_SOURCE_FORMAT.format(what=what)) as fd:
        author_documents = json.load(fd)

    print(f"{len(author_documents)} to index...")
    count = 0
    for author, document in author_documents.items():
        es_document = dict(document)
        es_document["id"] = slugify(author)
        es_document["author"] = author
        es_document["texts"] = list(prepare_texts(es_document["documents"]))
        es_document["texts_cut"] = list(shorten(es_document["texts"]))
        es_document["keywords"] = list(prepare_keywords(es_document["keywords"]))
        idx.index_single_document(es_document)
        count += 1

    print(f"{count} documents indexed so far.")


if __name__ == "__main__":
    what = sys.argv[-1]
    if what in ("person", "author", "author_ner"):
        index_authors_documents(what)
    else:
        print("please specify one of (person, author, author_ner)")
