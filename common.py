import glob


def list_files(folder=".", extension="*"):
    return glob.glob(f"{folder}/*.{extension}")
