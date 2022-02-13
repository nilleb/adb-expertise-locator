import requests
from common.io import read_object

all_faces = read_object("data/faces/all_faces_urls.json")
for url in all_faces:
    response = requests.request("GET", url)
    current = url.split('/')[-1]
    with open(f"data/faces/immages/{current}.png", "wb") as fd:
        fd.write(response.content)
