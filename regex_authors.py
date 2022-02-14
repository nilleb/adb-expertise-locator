import re
import logging
from common.folder_processor import DEFAULT_FOLDERS, FolderProcessor
from common.io import read_object, write_object
from common.filters import is_valid_author_name

AUTHOR_PAGE_DETECTOR = [
    "This report was prepared by a team consisting of",
    "Team leader",
]


DOCUMENT_ROLE_PATTERN = "(?P<documentRole>[ \-A-Za-z]+)"
FULLNAME_PATTERN = "(?P<fullname>([A-Z\. ])+ [A-Za-z \-]+)"
ORGANIZATION_PATTERN = "(?P<organization>\(?[A-Za-z ]+\)?)?"
ROLE_ALTERNATE_PATTERN = "(?P<role>[\- A-Za-z\(\)]+)"
AUTHOR_LINE_PATTERN = f"({DOCUMENT_ROLE_PATTERN}  )?(?P<fullname>[A-Za-z’\-\. ]+), {ROLE_ALTERNATE_PATTERN}[, ]*{ORGANIZATION_PATTERN}"
OPTIMIZED_PATTERN = re.compile(AUTHOR_LINE_PATTERN)

ROLE_PATTERN = "(?P<role>[ A-Za-z]+)"
FULLNAME_ALTERNATE_PATTERN = "(?P<fullname>(([A-Z]\.)|([A-Za-z]+))"
SINGLE_LINE_AUTHOR = f"{FULLNAME_PATTERN}(\({ROLE_PATTERN}\))?"
SINGLE_LINE_AUTHOR_ALTERNATE = f"{FULLNAME_ALTERNATE_PATTERN} [A-Za-z \-]+).*"

logging.basicConfig(level=logging.INFO)


def clean_author(author):
    author = author.strip()
    match = re.match(SINGLE_LINE_AUTHOR, author)
    if match:
        author_dict = {
            "fullname": match.group("fullname"),
        }
        if match.group("role"):
            author_dict["role"] = match.group("role")
        return author_dict


def clean_author_semicolon(author):
    match = re.match(SINGLE_LINE_AUTHOR_ALTERNATE, author)
    if match:
        author_dict = {
            "fullname": match.group("fullname"),
        }
        return author_dict


def extract_authors_from_single_line(page):
    match_single_line = "This report was prepared by a team consisting of"
    authors_line_began = False
    authors_line_tokens = []

    for line in page.split("\n"):
        idx = line.replace(match_single_line, "")
        if idx != line:
            authors_line_began = True
            line = idx
        if authors_line_began:
            authors_line_tokens.append(line)

    authors_line = " ".join([token.strip() for token in authors_line_tokens])
    authors_line = authors_line.replace(" and ", " ")

    authors_tokens = authors_line.split("; ")
    for author in authors_tokens:
        author_dict = clean_author_semicolon(author)
        if author_dict:
            yield author_dict

    authors_tokens = authors_line.split(", ")
    for author in authors_tokens:
        author_dict = clean_author(author)
        if author_dict:
            yield author_dict


def extract_authors_from_table(page):
    for line in page.split("\n"):
        match = OPTIMIZED_PATTERN.match(line)
        if match:
            fullname = match.group("fullname").strip()
            if not is_valid_author_name(fullname):
                continue

            author_dict = {
                "fullname": fullname,
                "role": match.group("role").strip(),
                "organization": (match.group("organization") or "").strip(),
            }
            yield author_dict


def is_author_page(path, page):
    for line in page.split("\n"):
        for match in AUTHOR_PAGE_DETECTOR:
            if match in line:
                logging.debug(f"{path} -> {line}")
                return True


def process_file(path):
    try:
        metadata = read_object(path)
    except:
        logging.exception(f"Caught unexpected exception while accessing {path}")
        return

    if metadata.get("authors"):
        return

    for page in metadata.get("pages", [])[:5]:
        if is_author_page(path, page):
            metadata["author_page"] = page
            metadata["authors"] = list(extract_authors_from_table(page))
            metadata["authors"].extend(list(extract_authors_from_single_line(page)))

    if metadata.get("authors"):
        logging.info(f"{path} yielded {len(metadata['authors'])} authors")
        write_object(metadata, path.replace(".metadata.", ".regex-authors."))
    else:
        logging.warning(f"{path} yielded 0 authors")


def test():
    test_lines = [
        "This report was prepared by a team consisting of E. Hassing (team leader), R. Clendon,  \nS. Hasnie, B. Lin, D. Millison, and M. Pajarillo. ",
        "This report was prepared by a team consisting of  Sangay Penjor, Project Team Leader; S. Popov, Project Specialist (Environment); X. Peng, Sr. Counsel; S. Ferguson, Resettlement Specialist; and Sheryl Guisihan, Administrative Assistant.",
    ]
    for line in test_lines:
        print(list(extract_authors_from_single_line(line)))


def test_file():
    print(process_file("data/input/reports/rrp-prc-33177.pdf.metadata.json"))
    print(process_file("data/input/reports/53314-001-rrp-en.pdf.metadata.json"))


def main(folders=None):
    if not folders:
        folders = DEFAULT_FOLDERS
    FolderProcessor(folders, "*.metadata.json", process_file).process_folders()


if __name__ == "__main__":
    main()
