import logging
import re

from common.folder_processor import FolderProcessor, process_single_file_holder, DEFAULT_FOLDERS


def process_single_object(metadata):
    document_words_count = 0
    for page in metadata.get("pages", []):
        words = re.split("\s", page)
        document_words_count += len(words)
    ner_count = 0
    for page in metadata.get("stanford_ner_pages", []):
        ner_count += len(page)
    if document_words_count != ner_count:
        logging.warning(f"{ner_count} != {document_words_count}")


if __name__ == "__main__":
    print("this analysis is performed on *.stanford_ner.json documents")
    FolderProcessor(
        DEFAULT_FOLDERS,
        "*.stanford_ner.json",
        process_single_file_holder(process_single_object),
    ).process_folders()
