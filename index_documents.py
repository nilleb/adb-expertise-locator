import logging
import os
import sys
import re

from backends.es import IndexingException, create_indexer
from common.constants import SETS_FILEPATH
from common.io import read_object, write_object
from configuration import LIMIT
from regex_authors import is_author_page

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

logging.basicConfig(level=logging.INFO)

import urllib3

urllib3.disable_warnings()

DOCUMENTS_SOURCE_FORMAT = "data/output/{what}.json"

idx = create_indexer()

stop_words = set(stopwords.words("english"))


def exclude_stop_words(text):
    word_tokens = word_tokenize(text)
    filtered_sentence = [w for w in word_tokens if not w.lower() in stop_words]
    return " ".join(filtered_sentence)


def lemmatize(text):
    lemma = nltk.wordnet.WordNetLemmatizer()
    word_tokens = word_tokenize(text)
    return " ".join([lemma.lemmatize(w) for w in word_tokens])


def squeeze(text):
    return re.sub("\s+", " ", text)


def shorten(texts):
    residual_len = LIMIT - 1
    for text in texts:
        text = exclude_stop_words(squeeze(text))
        logging.info(len(text))
        yield text[:residual_len]
        residual_len -= len(text) + 1
        if residual_len < 0:
            return


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
    sets = read_object(SETS_FILEPATH)
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


def index_single_document(document):
    es_document = dict(document)
    filenames = get_filenames(es_document["links"])
    es_document["texts"] = list(prepare_texts(es_document["links"]))
    es_document["links"] = get_links(filenames)
    es_document["texts_cut"] = list(shorten(es_document["texts"]))
    es_document["keywords"] = list(prepare_keywords(es_document["keywords"]))
    idx.index_single_document(es_document)


REMEMBER_PATH = "data/intermediate/indexed_documents.json"
try:
    INDEXED_DOCUMENTS = set(read_object(REMEMBER_PATH))
except:
    INDEXED_DOCUMENTS = set()


def should_process(document):
    return document["id"] not in INDEXED_DOCUMENTS


def remember(document):
    INDEXED_DOCUMENTS.add(document["id"])
    write_object(list(INDEXED_DOCUMENTS), REMEMBER_PATH)


REMEMBER_ERRORS_PATH = "data/intermediate/failed_indexing_documents.json"
try:
    FAILED_DOCUMENTS = set(read_object(REMEMBER_ERRORS_PATH))
except:
    FAILED_DOCUMENTS = set()


def remember_error(document):
    FAILED_DOCUMENTS.add(document["id"])
    write_object(list(FAILED_DOCUMENTS), REMEMBER_ERRORS_PATH)


def index_authors_documents(what):
    idx.setup_index()

    author_documents = read_object(DOCUMENTS_SOURCE_FORMAT.format(what=what))

    logging.info(f"{len(author_documents)} total documents loaded")

    for count, document in enumerate(author_documents.values()):
        if should_process(document):
            try:
                index_single_document(document)
                remember(document)
            except IndexingException:
                remember_error(document)

    logging.info(f"{count + 1} documents indexed.")


if __name__ == "__main__":
    what = sys.argv[-1] if len(sys.argv) == 1 else sys.argv[-2]
    who = sys.argv[-1] if len(sys.argv) == 3 else None
    if not who and what in ("regex-authors", "stanford_ner", "special-guests"):
        logging.info(f"indexing all {what} documents")
        index_authors_documents(what)
    else:
        author_documents = read_object(
            DOCUMENTS_SOURCE_FORMAT.format(what=what)
        )
        document = author_documents.get(who)
        if document:
            logging.info(f"indexing {what}/{who}")
            index_single_document(document)
        else:
            logging.error(f"not found: {what}/{who}")
