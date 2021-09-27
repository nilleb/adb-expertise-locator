#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glob
import json
import os

from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize

TAGGER = StanfordNERTagger(
    "/Users/nilleb/Downloads/stanford-ner-2020-11-17/classifiers/english.all.3class.distsim.crf.ser.gz",
    "/Users/nilleb/Downloads/stanford-ner-2020-11-17/stanford-ner-4.2.0.jar",
    encoding="utf-8",
)


def classify(text):
    tokenized_text = word_tokenize(text)
    return TAGGER.tag(tokenized_text)


def process_folders(folders):
    for folder in folders:
        if os.path.exists(folder) and os.path.isdir(folder):
            print(f"processing {folder}")
        else:
            print(f"skipping {folder}")
            continue

        paths = glob.glob(f"{folder}/*.metadata.json")
        for idx, path in enumerate(paths):
            print(f"({idx}/{len(paths)}) extracting named entities from {path}")
            classified_path = path.replace(".metadata.json", ".classified.json")
            if os.path.exists(path) and not os.path.exists(classified_path):
                with open(path) as fd:
                    metadata = json.load(fd)

                metadata["classified_text"] = classify(metadata.get("content", ""))
                author_pages = metadata.get("author_pages", "")
                metadata["classified_author_pages"] = classify("".join(author_pages))

                with open(classified_path, "w") as fd:
                    print(f"writing {classified_path}")
                    json.dump(metadata, fd)


if __name__ == "__main__":
    folders = ["data/input/pdf-generic", "data/input/technical", "data/input/reports"]
    process_folders(folders)
