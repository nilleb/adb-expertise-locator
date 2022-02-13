from common.folder_processor import FolderProcessor
from common.io import read_object, write_object
files = set()
faces = set()

def process_file(fpath):
    files.add(fpath)
    faces_response = read_object(fpath)
    for face in faces_response.get('faces', []):
        for url in face.get('urls', []):
            photo = url.get('512')
            if photo:
                faces.add(photo)


folders = ["data/faces"]
FolderProcessor(folders, "page*.json", process_file).process_folders()
print(f"{len(files)} -> {len(faces)}")
write_object(list(faces), "data/faces/all_faces_urls.json")
