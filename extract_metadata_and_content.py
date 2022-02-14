import glob
import logging
import os
from json import JSONEncoder

import pdfplumber

from common.folder_processor import DEFAULT_FOLDERS, FolderProcessor
from common.io import safe_read_object, write_object


class Document(object):
    def __init__(self, path):
        self.path = path
        self.pages = []
        try:
            with pdfplumber.open(path) as pdf:
                self.metadata = pdf.metadata
                for page_idx, page in enumerate(pdf.pages):
                    try:
                        text = page.extract_text()
                    except ValueError:
                        logging.exception(
                            "Unexpected exception caught while extracting "
                            f"page {page_idx} of document {path}."
                        )
                        text = ""
                    self.pages.append(text)
        except:
            logging.exception(f"Unexpected exception caught while reading {path}.")


class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def should_process_document(filepath):
    if not os.path.exists(filepath):
        return True

    document = safe_read_object(filepath, {})

    if document.get("path") and document.get("pages") and document.get("metadata"):
        return False

    return True


def process_single_file(path):
    metadata_path = f"{path}.metadata.json"
    if should_process_document(metadata_path):
        write_object(Document(path), metadata_path, cls=MyEncoder)


def main(folders=None):
    if not folders:
        folders = DEFAULT_FOLDERS
    FolderProcessor(folders, "*.pdf", process_single_file).process_folders()


if __name__ == "__main__":
    main()
