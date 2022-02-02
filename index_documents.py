import logging
import sys
import os
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


def pages_after_author_page(path, doc):
    begin_yield = False
    for page in doc.get("pages"):
        if begin_yield:
            yield page
        if not begin_yield and is_author_page(path, page):
            begin_yield = True


def prepare_texts(paths):
    for path in paths:
        doc = read_object(f"{path}.metadata.json")
        yield " ".join(pages_after_author_page(path, doc))


def prepare_keywords(keywords):
    for keyword, count in keywords.items():
        yield {"keyword": keyword, "count": count}


def load_report_names():
    sets = read_object("data/intermediate/sets.json")
    return {os.path.basename(path): path for path in sets.get("reports")}


REPORT_NAMES = load_report_names()


def get_filenames(links):
    filenames = [os.path.basename(document) for document in links]
    filenames = list(set(filenames))
    return filenames


def get_links(filenames):
    def short_id(filename):
        return filename.split("-")[0]

    def get_report(filename):
        return REPORT_NAMES.get(
            filename,
            f"https://www.adb.org/sites/default/files/project-documents/{short_id(filename)}/{filename}",
        )

    return [get_report(filename) for filename in filenames]


def index_authors_documents(what):
    idx.setup_index()

    author_documents = read_object(DOCUMENTS_SOURCE_FORMAT.format(what=what))

    logging.info(f"{len(author_documents)} total documents loaded")

    count = 0
    for document in author_documents.values():
        es_document = dict(document)
        filenames = get_filenames(es_document["links"])
        es_document["texts"] = list(prepare_texts(es_document["links"]))
        es_document["links"] = get_links(filenames)
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
