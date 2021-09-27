import json
import os
from urllib.parse import urlparse

import requests
from requests.exceptions import ChunkedEncodingError, SSLError


def build_sets():
    sets = {}

    if os.path.exists('data/intermediate/sets.json'):
        with open('data/intermediate/sets.json') as fd:
            sets = json.load(fd)

    if not sets:
        filenames = ['pdf-generic', 'technical', 'reports']
        for filename in filenames:
            if os.path.exists(f'{filename}.txt'):
                print(f"{filename}.txt")
                with open(f"{filename}.txt") as fd:
                    current = set()
                    for line in fd:
                        current.add(line.rstrip())
                    sets[filename] = list(current)

        with open("data/intermediate/sets.json", "w") as fd:
            json.dump(sets, fd)

    return sets


def get_filename(url):
    fn = os.path.basename(urlparse(url).path)
    fn = fn if fn.endswith('.pdf') else f"{fn}.pdf"
    return fn


def download_item_set(folder, urls):
    errors = []
    total, count = len(urls), 0
    for url in urls:
        count += 1
        path = f'{folder}/{get_filename(url)}'
        print(f"({count}/{total}) -> {path} (exists? {os.path.exists(path)})")
        if not os.path.exists(path):
            try:
                response = requests.get(url)
            except (ChunkedEncodingError, SSLError):
                errors.append(url)
                print(f"error caught downloading {url}")
                continue
            with open(path, 'wb') as f:
                f.write(response.content)
    return errors

def download_and_retry_once(key, urls):
    print(f"downloading {key}")
    if not os.path.exists(key):
        os.mkdir(key)
    download_set = urls
    while download_set:
        download_set_post = download_item_set(key, download_set)
        download_set = list(set(download_set_post) - set(download_set))


if __name__ == '__main__':
    sets = build_sets()
    for key, urls in sets.items():
        download_and_retry_once(key, urls)
