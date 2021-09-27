# get all the PERSON objects in the metadata
# create a dictionary with PERSON -> documents

# try to extract concepts from the text
import glob
import json
import re
from collections import defaultdict

SKIPPED_WORDS = set(
    [
        "SERD",
        "SARD",
        "Tel",
        "CWRD",
        "PARD",
        "EARD",
        "CWRDa",
        "OSFMD",
        "PSOD",
        "LGED",
        "CAAN",
    ]
)
SKIPPED_KEYWORDS = set(
    [
        "and",
        "of",
        "the",
        "recommendation",
        "president",
        "adb",
        "rrp",
        "report",
        "projects",
        "asian",
        "development",
        "bank",
        "approval",
        "recommendations",
    ]
)
FULLNAME_PATTERN = "(?P<fullname>([A-Z\. ])+ [A-Za-z \-]+)"
ROLE_PATTERN = "(?P<role>[ A-Za-z]+)"
ORGANIZATION_PATTERN = "(?P<organization>\(?[A-Za-z ]+\)?)?"
AUTHOR_LINE_PATTERN = f"{FULLNAME_PATTERN},{ROLE_PATTERN}[, ]*{ORGANIZATION_PATTERN}"
OPTIMIZED_PATTERN = re.compile(AUTHOR_LINE_PATTERN)


def read_content(path):
    with open(path) as fd:
        return json.load(fd)


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj, encoding="utf-8", errors="replace")
        return json.JSONEncoder.default(self, obj)


def save_object(obj, path, kind="w"):
    with open(path, kind) as fd:
        return json.dump(obj, fd, cls=MyEncoder)


def extract_persons(document, key="classified_text"):
    persons, current_person = [], []
    for token, kind in document[key]:
        if kind != "PERSON":
            if current_person:
                persons.append(" ".join(current_person))
                current_person = []
        if kind == "PERSON":
            if token in SKIPPED_WORDS:
                continue
            current_person.append(token)
    return persons


def extract_authors(document):
    for textbox in document.get("author_pages", []):
        lines = textbox.split("\n")
        authors = []
        for line in lines:
            match = OPTIMIZED_PATTERN.match(line)
            if match:
                authors.append(
                    {
                        "fullname": match.group("fullname"),
                        "role": match.group("role"),
                        "organization": match.group("organization"),
                    }
                )
        if 1.0 * len(authors) / len(lines) > 0.3:
            print(authors)
            return authors

    return []


def extract_ner_authors(document):
    return extract_persons(document, "classified_author_pages")


def extract_keywords(document):
    keywords = defaultdict(int)
    dk = document.get("Keywords", "").split(" ")
    for keyword in dk:
        keyword = keyword.strip(" ,\n;")
        if keyword and keyword not in SKIPPED_KEYWORDS:
            keywords[keyword] += 1
    return keywords


def populate_index(index, document_path, document_people, document_keywords, document):
    for person in document_people:
        person_key = person.get("fullname") if isinstance(person, dict) else person
        person_document = index.get(person_key, {})

        documents = person_document.get("documents", [])
        documents.append(document_path.replace(".classified.json", ""))

        texts = person_document.get("texts", [])
        # texts.append(document.get("content"))

        keywords = person_document.get("keywords", defaultdict(int))
        for key, count in document_keywords.items():
            keywords[key] += count

        index[person_key] = {
            "keywords": keywords,
            "documents": documents,
            "texts": texts,
        }


def build_people_indexes(folders):
    person_documents = {}
    author_documents = {}
    author_ner_documents = {}
    all_persons = []
    all_authors = []
    all_authors_ner = []

    for folder in folders:
        filepaths = glob.glob(f"{folder}/*.classified.json")
        for idx, path in enumerate(filepaths):
            print(f"({idx+1}/{len(filepaths)}) {path}")
            document = read_content(path)

            document_persons = extract_persons(document)
            document_authors = extract_authors(document)
            document_ner_authors = extract_ner_authors(document)
            document_keywords = extract_keywords(document)

            all_persons.extend(document_persons)
            all_authors.extend(document_authors)
            all_authors_ner.extend(document_ner_authors)

            populate_index(
                person_documents, path, document_persons, document_keywords, document
            )
            populate_index(
                author_documents, path, document_authors, document_keywords, document
            )
            populate_index(
                author_ner_documents,
                path,
                document_ner_authors,
                document_keywords,
                document,
            )

    save_object(person_documents, "data/intermediate/person_documents.json")
    save_object(author_documents, "data/intermediate/author_documents.json")
    save_object(author_ner_documents, "data/intermediate/author_ner_documents.json")
    save_object(all_persons, "data/intermediate/all_persons.json")
    save_object(all_authors, "data/intermediate/all_authors.json")
    save_object(all_authors_ner, "data/intermediate/all_authors_ner.json")
    print(f"{len(all_persons)}, {len(all_authors)}, {len(all_authors_ner)}")

    aps, ans = set(all_persons), set(all_authors_ner)
    aas = set([author.get("fullname") for author in all_authors])
    intersect = aps.intersection(aas).intersection(ans)
    print(f"{len(intersect)}")


if __name__ == "__main__":
    folders = ["data/input/reports"]
    build_people_indexes(folders)
