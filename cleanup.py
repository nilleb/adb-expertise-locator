import glob
import os

from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser, PDFSyntaxError

folder = "data/input/reports"
paths = glob.glob(f"{folder}/*.pdf")
for path in paths:
    with open(path, 'rb') as fd:
        parser = PDFParser(fd)
        try:
            doc = PDFDocument(parser)
        except PDFSyntaxError as err:
            os.unlink(path)
