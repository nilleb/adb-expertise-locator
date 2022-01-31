import glob
import json
import logging
import os
from json import JSONEncoder

import pdfplumber


class Document(object):
    def __init__(self, path):
        self.path = path
        self.pages = []
        with pdfplumber.open(path) as pdf:
            self.metadata = pdf.metadata
            for page in pdf.pages:
                self.pages.append(page.extract_text())


class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def process_folders(folders):
    for folder in folders:
        if os.path.exists(folder) and os.path.isdir(folder):
            print(f"processing {folder}")
        else:
            print(f"skipping {folder}")
            continue
        process_folder(folder)


def should_process_document(filepath):
    if not os.path.exists(filepath):
        return True

    with open(filepath) as fd:
        try:
            document = json.load(fd)
        except json.decoder.JSONDecodeError:
            return True

    if document.get("path") and document.get("pages") and document.get("metadata"):
        return False

    return True


def process_folder(folder):
    paths = glob.glob(f"{folder}/*.pdf")
    for idx, path in enumerate(paths):
        print(f"({idx+1}/{len(paths)}) extracting metadata and text from {path}")
        metadata_path = f"{path}.metadata.json"
        if should_process_document(metadata_path):
            with open(metadata_path, "w") as fd:
                try:
                    json.dump(Document(path), fd, cls=MyEncoder)
                except:
                    logging.exception(f"exception caught processing: {path}")


def describe(folders):
    documents = {"processed": 0, "not_processed": []}
    for folder in folders:
        paths = glob.glob(f"{folder}/*.pdf.metadata.json")
        for path in paths:
            if should_process_document(path):
                documents["processed"] += 1
            else:
                documents["not_processed"].append(path)
    for key, value in documents.items():
        print(f"{key}: {value}" if isinstance(value, int) else f"{key}: {len(value)}")
    with open("describe_metadata.json", "w") as fd:
        json.dump(documents, fd)


if __name__ == "__main__":
    folders = ["data/input/pdf-generic", "data/input/technical", "data/input/reports"]
    process_folders(folders)
    describe(folders)
