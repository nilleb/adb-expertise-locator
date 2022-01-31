from collections import defaultdict
from common.folder_processor import FolderProcessor
from common.io import read_object, write_object

author_reports = defaultdict(list)

def process_file(filepath):
    metadata = read_object(filepath)
    for author in metadata.get('authors'):
        author_reports[author.get('fullname')].append(filepath)

if __name__ == "__main__":
    folders = ["data/input/pdf-generic", "data/input/technical", "data/input/reports"]
    FolderProcessor(folders, "*.regex-authors.json", process_file).process_folders()
    write_object(author_reports, "describe_authors.json")
    for a, b in sorted(author_reports.items(), key=lambda kv: (len(kv[1]), kv[0])):
        print(f"{a}, {len(b)}")
    print(f"=> {len(author_reports)} authors are mentioned in the analyzed reports.")