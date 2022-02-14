import os
from collections import defaultdict
from common.folder_processor import FolderProcessor

paths = defaultdict(set)
files = set()


def process_single_file(path):
    basename = path.split("/")[-1]
    paths[basename].add(path)
    files.add(path)


def cleanup_orphans(path):
    pdf_file = path.split(".pdf")[0] + ".pdf"
    if not os.path.exists(pdf_file):
        os.unlink(path)


def main():
    FolderProcessor(["data/input"], "**/*.pdf", process_single_file).process_folders()
    print(f"{len(files)} files, {len(paths)} unique basenames")

    for file, path_list in paths.items():
        for path in list(path_list)[1:]:
            os.unlink(path)

    FolderProcessor(["data/input/"], "**/*.json", cleanup_orphans).process_folders()


if __name__ == "__main__":
    main()
