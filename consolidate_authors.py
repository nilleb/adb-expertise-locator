import hashlib
import sys
from slugify import slugify
from statistics.describe_keywords import split_keywords
from common.io import read_object, write_object
from common.folder_processor import FolderProcessor, DEFAULT_FOLDERS

KEYS = ["regex", "stanford_ner"]
PATTERNS = {"regex": "regex-authors", "stanford_ner": "stanford_ner"}
ATTRIBUTES = {"regex": "authors", "stanford_ner": "stanford_ner_authors"}

def add_or_update_author(
    filepath, metadata, author, storage, key="regex"
):  # or stanford_ner
    fullname = author.get("fullname")
    author = storage.get(fullname, author)

    links = author.get("links", [])
    links.append(filepath.replace(f".{PATTERNS[key]}.json", ""))
    author["links"] = list(set(links))

    keywords = author.get("keywords", {})
    for keyword in metadata.get("keywords"):
        keywords[keyword] = keywords.get(keyword, 0) + 1
    author["keywords"] = keywords

    storage[fullname] = author


def process_single_object(
    metadata, filepath, storage, key="regex"
):  # or stanford_ner_authors
    for author in metadata.get(ATTRIBUTES[key]):
        add_or_update_author(
            filepath,
            metadata,
            author,
            storage,
            key,
        )


def process_single_file_holder(storage, key):
    def process_single_file(path):
        try:
            metadata = read_object(path)
        except:
            return

        document_keywords = split_keywords(metadata)
        document_keywords = [
            keyword.lower() for keyword in document_keywords if keyword
        ]
        metadata["keywords"] = document_keywords

        process_single_object(metadata, path, storage, key)

        # write_object(metadata, path.replace(f".PATTERNS[key].json", ".complete.json"))

    return process_single_file


def complete_author_document(fullname, document):
    uid = slugify(fullname)
    encoded = hashlib.md5(uid.encode("utf-8")).hexdigest()
    number = int(encoded[6:12], 16)
    document["telephoneNumber"] = f"555-{number}"
    document["email"] = f"{uid}@adb.nilleb.com"
    document["id"] = uid


def main(folders=None):
    if len(sys.argv) > 1:
        key = sys.argv[1]
        assert key in KEYS
    else:
        key = "regex"

    storage = {}

    if not folders:
        folders = DEFAULT_FOLDERS

    FolderProcessor(
        folders, f"*.{PATTERNS[key]}.json", process_single_file_holder(storage, key)
    ).process_folders()

    for fullname, document in storage.items():
        complete_author_document(fullname, document)

    path = f"data/output/{PATTERNS[key]}.json"
    write_object(storage, path)
    print(f"{len(storage)} authors exported to {path}.")


if __name__ == "__main__":
    main()
