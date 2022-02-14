#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import logging

from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
from common.filters import is_valid_author_name

from common.folder_processor import DEFAULT_FOLDERS, FolderProcessor
from common.io import write_object

TAGGER = StanfordNERTagger(
    "data/models/stanford_ner/english.all.3class.distsim.crf.ser.gz",
    "data/models/stanford_ner/stanford-ner.jar",
    encoding="utf-8",
)

SKIPPED_WORDS = set(
    [
        "SERD",
        "SARD",
        "Tel",
        "CWRD",
        "PARD",
        "EARD",
        "CWRDa",
        "OSFMD",
        "PSOD",
        "LGED",
        "CAAN",
    ]
)


def classify(text):
    tokenized_text = word_tokenize(text)
    return TAGGER.tag(tokenized_text)


def process_single_file(path):
    classified_path = path.replace(".regex-authors.json", ".stanford_ner.json")
    if os.path.exists(path) and not os.path.exists(classified_path):
        with open(path) as fd:
            metadata = json.load(fd)

        process_single_object(metadata)

        write_object(metadata, classified_path)


def extract_persons(classified_text):
    persons, current_person = [], []
    for token, kind in classified_text:
        if kind != "PERSON":
            if current_person:
                persons.append(" ".join(current_person))
                current_person = []
        if kind == "PERSON":
            if token in SKIPPED_WORDS:
                continue
            current_person.append(token)
    return persons


def format_author(fullname):
    return {"fullname": fullname}


def process_single_object(metadata):
    pages, author_page, classified_authors_page, authors_page_idx = (
        [],
        metadata.get("author_page"),
        None,
        0,
    )
    for idx, page in enumerate(metadata.get("pages", [])):
        classified_page = classify(page)
        pages.append(classified_page)
        if page[:1000] == author_page[:1000] and author_page:
            classified_authors_page = classified_page
            authors_page_idx = idx
    metadata["stanford_ner_pages"] = pages
    metadata["stanford_ner_author_page"] = classified_authors_page
    authors = [
        format_author(person)
        for person in extract_persons(classified_authors_page)
        if is_valid_author_name(person)
    ]
    if len(authors) != len(metadata.get("authors")):
        logging.warning(f"{len(authors)} != {len(metadata.get('authors'))}")
    metadata["stanford_ner_authors"] = authors
    metadata["author_page_idx"] = authors_page_idx
    return metadata


def main(folders=None):
    if not folders:
        folders = DEFAULT_FOLDERS
    FolderProcessor(
        folders, "*.regex-authors.json", process_single_file
    ).process_folders()


if __name__ == "__main__":
    main()
