import logging
import os
import glob

from .io import read_object

from configuration import configuration

DEFAULT_FOLDERS = configuration.get("folder_processor", {}).get("folders", [])


def process_single_file_holder(fun=None):
    def process_single_file(filepath):
        if fun:
            metadata = read_object(filepath)
            fun(metadata)

    return process_single_file


class FolderProcessor(object):
    def __init__(self, folders, pattern, process_single_file) -> None:
        super().__init__()
        self.folders = folders
        self.pattern = pattern
        self.process_single_file = process_single_file

    def process_folder(self, folder):
        paths = glob.glob(f"{folder}/{self.pattern}")
        for idx, path in enumerate(paths):
            print(f"({idx+1}/{len(paths)}) processing {path}")
            self.process_single_file(path)

    def process_folders(self):
        for folder in self.folders:
            if os.path.exists(folder) and os.path.isdir(folder):
                logging.info(f"processing {folder}")
            else:
                logging.info(f"skipping {folder}")
                continue
            self.process_folder(folder)
