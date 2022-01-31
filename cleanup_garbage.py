import os
from common.folder_processor import FolderProcessor
from common.io import read_object

def process_file(filepath):
    if not os.path.exists(filepath.replace('.metadata.json', '')):
        metadata = read_object(filepath)
        if not metadata.get('pages'):
            os.unlink(filepath)

if __name__ == "__main__":
    folders = ["data/input/pdf-generic", "data/input/technical", "data/input/reports"]
    FolderProcessor(folders, "*.metadata.json", process_file).process_folders()
