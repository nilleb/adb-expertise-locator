from collections import defaultdict
from common.folder_processor import DEFAULT_FOLDERS, FolderProcessor
from common.io import read_object, write_object

author_reports = defaultdict(list)
stanford_ner_author_reports = defaultdict(list)


def process_file(filepath):
    metadata = read_object(filepath)
    process_single_object(metadata, filepath)


def process_single_object(metadata, filepath):
    for author in metadata.get("authors"):
        author_reports[author.get("fullname")].append(filepath)
    for author in metadata.get("stanford_ner_authors"):
        stanford_ner_author_reports[author.get("fullname")].append(filepath)


def sort_dictionary_values(dico, fun=len):
    return sorted(dico.items(), key=lambda kv: (fun(kv[1]), kv[0]))


def get_stanford_ner_authors():
    return stanford_ner_author_reports


def get_regex_authors():
    return author_reports


if __name__ == "__main__":
    print("this analysis is performed on *.stanford_ner.json documents")
    folders = DEFAULT_FOLDERS
    FolderProcessor(folders, "*.stanford_ner.json", process_file).process_folders()

    print("10 most cited authors (regex)")
    sorted_authors = sort_dictionary_values(author_reports, fun=len)
    for a, b in sorted_authors[-10:]:
        print(f"{a}, {len(b)}")

    print("10 most cited authors (Stanford NER)")
    sorted_authors_stanford = sort_dictionary_values(
        stanford_ner_author_reports, fun=len
    )
    for a, b in sorted_authors_stanford[-10:]:
        print(f"{a}, {len(b)}")

    print(
        f"=> {len(author_reports)} authors are mentioned in the reports anayzed with regex."
    )
    print(
        f"=> {len(stanford_ner_author_reports)} authors are mentioned in the reports analyzed with Stanford NER."
    )
    snset = set(stanford_ner_author_reports.keys())
    rxset = set(author_reports.keys())
    print(f"=> the intersection has {len(rxset.intersection(snset))} items")
    print("=> the first ten elements in regex that can not be found in stanford ner")
    for item in list(rxset.difference(snset))[:10]:
        print(item)
    print("=> the first ten elements in stanford ner that can not be found in regex")
    for item in list(snset.difference(rxset))[:10]:
        print(item)

    data = {
        "authors_regex": author_reports,
        "authors_stanford_ner": stanford_ner_author_reports,
    }
    write_object(data, "data/intermediate/describe/describe_authors.json")
