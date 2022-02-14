from common.folder_processor import DEFAULT_FOLDERS, FolderProcessor
from common.io import read_object, write_object, MyEncoder

# Title <class 'str'> 502
# content <class 'str'> 536
# Author <class 'str'> 515
# CreationDate <class 'str'> 535
# Creator <class 'str'> 519
# Keywords <class 'str'> 442
# ModDate <class 'str'> 533
# Producer <class 'str'> 530

DATA = {}
authors = set()


def process_single_file(path):
    document = read_object(path)
    content = "".join(document.get("pages", []))
    metadata = document.get("metadata", {})
    keywords = metadata.get("Keywords")
    title = metadata.get("Title")
    autnors_count = len(document.get("authors", []))
    DATA[path] = {
        "has_content": bool(content),
        "has_keywords": bool(keywords),
        "has_title": bool(title),
        "authors_count": autnors_count,
    }
    for author in document.get("authors", []):
        authors.add(author.get("fullname"))


total_pdfs = set()


def count(path):
    total_pdfs.add(path)


analysis_path = "data/intermediate/describe/complete_documents.json"

folders = DEFAULT_FOLDERS
FolderProcessor(folders, "*.regex-authors.json", process_single_file).process_folders()
write_object(DATA, analysis_path, cls=MyEncoder)
FolderProcessor(folders, "*.pdf", count).process_folders()

print(
    f"recognized {len(DATA)} documents (over {len(total_pdfs)} PDFs), {len(authors)} authors"
)
# recognized 6232 documents (over 9094 PDFs), 7079 authors
