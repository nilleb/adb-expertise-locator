#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os

from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize

from common.folder_processor import FolderProcessor
from common.io import write_object

TAGGER = StanfordNERTagger(
    "/Users/nilleb/Downloads/stanford-ner-2020-11-17/classifiers/english.all.3class.distsim.crf.ser.gz",
    "/Users/nilleb/Downloads/stanford-ner-2020-11-17/stanford-ner-4.2.0.jar",
    encoding="utf-8",
)


def classify(text):
    tokenized_text = word_tokenize(text)
    return TAGGER.tag(tokenized_text)


def process_single_file(path):
    classified_path = path.replace(".regex-authors.json", ".classified.json")
    if os.path.exists(path) and not os.path.exists(classified_path):
        with open(path) as fd:
            metadata = json.load(fd)

        text = " ".join(metadata.get("pages", []))
        metadata["classified_text"] = classify(text)
        author_page = metadata.get("author_page", "")
        metadata["classified_author_page"] = classify("".join(author_page))

        write_object(metadata, classified_path)


def main(folders=None):
    if not folders:
        folders = ["data/input/pdf-generic", "data/input/technical", "data/input/reports"]
    FolderProcessor(
        folders, "*.regex-authors.json", process_single_file
    ).process_folders()


if __name__ == "__main__":
    main()
