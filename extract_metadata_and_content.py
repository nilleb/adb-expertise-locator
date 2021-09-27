import glob
import json
import logging
import os
from io import StringIO

from pdfminer.converter import PDFPageAggregator, TextConverter
from pdfminer.layout import LAParams, LTTextContainer
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser, PDFSyntaxError
from pdfminer.psparser import PSLiteral


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj, encoding="utf-8", errors="replace")
        if isinstance(obj, PSLiteral):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def get_pdf_content(doc):
    with StringIO() as output_string:
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            print(".", end="")
            interpreter.process_page(page)
        print("")
        return output_string.getvalue()


def get_pdf_pages_2_and_3(doc):
    resource_manager = PDFResourceManager()
    device = PDFPageAggregator(resource_manager, laparams=LAParams())
    interpreter = PDFPageInterpreter(resource_manager, device)
    for idx, page in enumerate(PDFPage.create_pages(doc)):
        if idx == 1 or idx == 2:
            interpreter.process_page(page)
            layout = device.get_result()
            for element in layout:
                if isinstance(element, LTTextContainer):
                    yield element.get_text()


def process_folders(folders):
    for folder in folders:
        if os.path.exists(folder) and os.path.isdir(folder):
            print(f"processing {folder}")
        else:
            print(f"skipping {folder}")
            continue
        process_folder(folder)


def extract_pdf_metadata_and_content(filepath, only_content=False, only_authors=False):
    with open(filepath, "rb") as fp:
        parser = PDFParser(fp)
        try:
            doc = PDFDocument(parser)
        except PDFSyntaxError as err:
            print(f"!!! Unable to read {filepath}: {err}")
            return {}

        if len(doc.info) > 1:
            print("unexpected: more than one PDF document info")
            print(doc.info)

        if doc.info:
            document = dict(doc.info[0])
        else:
            document = {}

        if not only_authors:
            content = get_pdf_content(doc)
            document["content"] = content

        if not only_content:
            author_pages = list(get_pdf_pages_2_and_3(doc))
            document["author_pages"] = author_pages

    return document


def should_process_document(filepath):
    if not os.path.exists(filepath):
        return True

    with open(filepath) as fd:
        try:
            document = json.load(fd)
        except json.decoder.JSONDecodeError:
            return True

    if document.get("content") and document.get("author_pages"):
        return False

    return True


def process_folder(folder):
    paths = glob.glob(f"{folder}/*.pdf")
    for idx, path in enumerate(paths):
        print(f"({idx+1}/{len(paths)}) extracting metadata and text {path}")
        metadata_path = f"{path}.metadata.json"
        if should_process_document(metadata_path):
            document = extract_pdf_metadata_and_content(path)

            with open(metadata_path, "w") as fd:
                try:
                    json.dump(document, fd, cls=MyEncoder)
                except:
                    logging.exception(f"exception caught processing {path}")


if __name__ == "__main__":
    folders = ["data/input/pdf-generic", "data/input/technical", "data/input/reports"]
    process_folders(folders)
