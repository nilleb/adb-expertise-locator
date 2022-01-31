import json
import os
from urllib.parse import urlparse
import logging

import requests
from requests.exceptions import ChunkedEncodingError, SSLError

logging.basicConfig(level=logging.INFO)


def build_sets():
    try:
        with open("data/intermediate/sets.json") as fd:
            sets = json.load(fd)

    except:
        sets = {}
        filenames = ["pdf-generic", "technical", "reports"]

        for filename in filenames:
            if os.path.exists(f"{filename}.txt"):
                logging.info(f"processing {filename}.txt")
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
    fn = fn if fn.endswith(".pdf") else f"{fn}.pdf"
    return fn


def download_file(url, path):
    try:
        response = requests.get(url)
    except (ChunkedEncodingError, SSLError):
        logging.error(f"error caught downloading {url}")
        yield url

    with open(path, "wb") as fd:
        fd.write(response.content)


def download_item_set(folder, urls):
    errors = []
    total, count = len(urls), 0
    for url in urls:
        count += 1
        path = f"data/input/{folder}/{get_filename(url)}"
        logging.info(f"({count}/{total}) -> {path} (exists? {os.path.exists(path)})")
        if not os.path.exists(path):
            to_retry = list(download_file(url, path))
            if to_retry:
                errors.extend(to_retry)
    return errors


def download_and_retry_once(key, urls):
    logging.info(f"downloading {key} ({len(urls)} urls)")
    if not os.path.exists(key):
        os.mkdir(key)
    download_set = urls
    while download_set:
        download_set_post = download_item_set(key, download_set)
        download_set = list(set(download_set_post) - set(download_set))


def filter_urls(urls):
    for url in urls:
        if "rrp" in url:
            yield url


if __name__ == "__main__":
    sets = build_sets()
    for key, urls in sets.items():
        download_and_retry_once(key, list(filter_urls(urls)))
