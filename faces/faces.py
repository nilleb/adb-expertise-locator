import requests
from common.io import write_object
from configuration import configuration

API_KEY = configuration.get('generated-photos-api-key')

url = "https://api.generated.photos/api/v1/faces"

for page in range(11, 24):
    querystring = {
        "age": "adult",
        "emotion": "joy",
        "per_page": "100",
        "page": str(page),
    }

    headers = {"user-agent": "vscode-restclient", "authorization": f"API-Key {API_KEY}"}

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)
    write_object(response.json(), f"data/faces/page_{page}.json")
