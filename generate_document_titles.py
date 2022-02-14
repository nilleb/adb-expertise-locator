import logging
from common.constants import SETS_FILEPATH
from common.folder_processor import DEFAULT_FOLDERS, FolderProcessor
from common.io import read_object, write_object
from common.filters import strip_unwanted

FILEPATH = "data/intermediate/documents.json"
DATA = {}
SETS = read_object(SETS_FILEPATH)
REPORT_URLS = {path.split("/")[-1]: path for path in SETS.get("reports")}


def short_id(filename):
    return filename.split("-")[0]

def process_file(path):
    try:
        metadata = read_object(path)
    except:
        logging.exception(f"Caught unexpected exception while accessing {path}")
        return
    filename = path.split("/")[-1].replace(".metadata.json", "")
    DATA[filename] = {
        "title": strip_unwanted(metadata.get("metadata", {}).get("Title") or ""),
        "subject": metadata.get("metadata", {}).get("Subject") or "",
        "url": REPORT_URLS.get(filename)
        or f"https://www.adb.org/sites/default/files/project-documents/{short_id(filename)}/{filename}",
    }


def main(folders=None):
    if not folders:
        folders = DEFAULT_FOLDERS
    FolderProcessor(folders, "*.metadata.json", process_file).process_folders()
    write_object(DATA, FILEPATH)


if __name__ == "__main__":
    main()
