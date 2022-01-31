import re
import json
from common.folder_processor import FolderProcessor
from common.io import read_object, write_object

matches = [
    "This report was prepared by a team consisting of",
    "Team leader"]

FULLNAME_PATTERN = "(?P<fullname>([A-Z\. ])+ [A-Za-z \-]+)"
ROLE_PATTERN = "(?P<role>[ A-Za-z]+)"
ORGANIZATION_PATTERN = "(?P<organization>\(?[A-Za-z ]+\)?)?"
AUTHOR_LINE_PATTERN = f"{FULLNAME_PATTERN},{ROLE_PATTERN}[, ]*{ORGANIZATION_PATTERN}"
OPTIMIZED_PATTERN = re.compile(AUTHOR_LINE_PATTERN)

def extract_authors(page):
    for line in page.split('\n'):
        match = OPTIMIZED_PATTERN.match(line)
        if match:
            yield {
                    "fullname": match.group("fullname"),
                    "role": match.group("role"),
                    "organization": match.group("organization"),
                }

def process_file(path):
    metadata = read_object(path)

    if metadata.get('authors'):
        return

    for page in metadata.get('pages')[:5]:
        for line in page.split('\n'):
            for match in matches:
                if match in line:
                    print(f'{path} -> {line}')
                    metadata['author_page'] = page
                    metadata['authors'] = extract_authors(page)

    if metadata.get('authors'):
        write_object(metadata, path)


if __name__ == "__main__":
    folders = ["data/input/pdf-generic", "data/input/technical", "data/input/reports"]
    FolderProcessor(folders, '*.metadata.json', process_file).process_folders()
