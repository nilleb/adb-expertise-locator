import logging
import sys
from common.io import read_object

from configuration import LIMIT
from backends.es import create_indexer
from regex_authors import is_author_page

logging.basicConfig(level=logging.INFO)


DOCUMENTS_SOURCE_FORMAT = "data/output/{what}.json"

idx = create_indexer()


def shorten(texts):
    for text in texts:
        cut = len(text) - LIMIT
        if cut > 0:
            text[:-cut]
        yield text


def pages_after_author_page(doc):
    begin_yield = False
    for page in enumerate(doc.get("pages")):
        if begin_yield:
            yield page
        if not begin_yield and is_author_page("dummy", page):
            begin_yield = True


def prepare_texts(documents):
    for document in documents:
        doc = read_object(f"data/input/{document}.metadata.json")
        yield " ".join(pages_after_author_page(doc))


def prepare_keywords(keywords):
    for keyword, count in keywords.items():
        yield {"keyword": keyword, "count": count}


def index_authors_documents(what):
    idx.setup_index()

    author_documents = read_object(DOCUMENTS_SOURCE_FORMAT.format(what=what))

    logging.info(f"{len(author_documents)} total documents loaded")

    count = 0
    for document in author_documents.values():
        es_document = dict(document)
        es_document["links"] = es_document["links"]
        es_document["texts"] = list(prepare_texts(es_document["links"]))
        es_document["texts_cut"] = list(shorten(es_document["texts"]))
        es_document["keywords"] = list(prepare_keywords(es_document["keywords"]))
        idx.index_single_document(es_document)
        count += 1

    logging.info(f"{count} documents indexed.")


if __name__ == "__main__":
    what = sys.argv[-1]
    if what in ("regex-authors", "stanford_ner"):
        index_authors_documents(what)
    else:
        print("please specify one of (regex-authors, stanford_ner)")
