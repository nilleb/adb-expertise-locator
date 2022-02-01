import hashlib
from slugify import slugify
from statistics.describe_keywords import split_keywords
from common.io import read_object, write_object
from common.folder_processor import FolderProcessor, DEFAULT_FOLDERS

regex_author_data = {}
stanford_ner_author_data = {}

def add_or_update_author(filepath, metadata, author, storage):
    fullname = author.get("fullname")
    author = storage.get(fullname, author)

    links = author.get('links', [])
    links.append(filepath.replace('.stanford_ner.json', ''))
    author['links'] = links

    keywords = author.get('keywords', {})
    for keyword in metadata.get('keywords'):
        keywords[keyword] = keywords.get(keyword, 0) + 1
    author['keywords'] = keywords

    storage[fullname] = author

def process_single_object(metadata, filepath):
    for author in metadata.get("authors"):
        add_or_update_author(filepath, metadata, author, regex_author_data)
    for author in metadata.get("stanford_ner_authors"):
        add_or_update_author(filepath, metadata, author, stanford_ner_author_data)


def process_single_file(path):
    try:
        metadata = read_object(path)
    except:
        return

    document_keywords = split_keywords(metadata)
    document_keywords = [keyword.lower() for keyword in document_keywords if keyword]
    metadata["keywords"] = document_keywords

    process_single_object(metadata, path)

    write_object(metadata, path.replace(".stanford_ner.json", ".complete.json"))


def complete_author_document(fullname, document):
    uid = slugify(fullname)
    encoded = hashlib.md5(uid.encode("utf-8")).hexdigest()
    number = int(encoded[6:12], 16)
    document["telephoneNumber"] = f"555-{number}"
    document["email"] = f"{uid}@adb.nilleb.com"


    
def main(folders=None):
    if not folders:
        folders = DEFAULT_FOLDERS
    FolderProcessor(
        folders, "*.stanford_ner.json", process_single_file
    ).process_folders()

    for fullname, document in regex_author_data.items():
        complete_author_document(fullname, document)
    for fullname, document in stanford_ner_author_data.items():
        complete_author_document(fullname, document)

    write_object(regex_author_data, 'data/output/regex_authors.json')
    write_object(stanford_ner_author_data, 'data/output/ner_authors.json')

if __name__ == "__main__":
    main()
