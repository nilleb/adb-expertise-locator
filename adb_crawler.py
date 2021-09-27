# download pdf from adb.org public data
# https://www.adb.org/projects/documents/rss?terms=report%20and%20recommendation%20to%20the%20president&sort_by=field_date_content&sort_order=ASC&page=121
# https://www.adb.org/projects/documents?terms=recommendation%20to%20the%20president&page=122

import json
# div.list/div.item/div.item-title/a@href
import os

import requests
from bs4 import BeautifulSoup


def generate_links():
    if os.path.exists("data/intermediate/links.json"):
        with open("data/intermediate/links.json") as fd:
            urls = json.load(fd)
    else:
        urls, pdfs = [], []

        for page in range(1, 127):
            url = f"https://www.adb.org/projects/documents?terms=recommendation%20to%20the%20president&page={page}"
            html_text = requests.get(url).text
            soup = BeautifulSoup(html_text, "html.parser")
            divs = soup.find_all("div", class_="item-title")
            for div in divs:
                urls.append(list(div.children)[0]["href"])

        for url in urls:
            html_text = requests.get(url).text
            soup = BeautifulSoup(html_text, "html.parser")
            elem = soup.find_all("a", class_="downloads")
            if not elem:
                print(f"{url}: no elem found")
                continue
            pdfs.append(elem[0]["href"])

        with open("data/intermediate/links.json", "w") as fd:
            json.dump(pdfs, fd)

    return urls


def complete_url(url):
    return url if "www.adb.org" in url else f"https://www.adb.org{url}"


def crawl():
    urls = generate_links()
    print(f"downloaded {len(urls)} pdfs")
    sets = {"reports": [complete_url(url) for url in urls]}
    return sets


if __name__ == "__main__":
    sets = crawl()
    with open("data/intermediate/sets.json", "w") as fd:
        json.dump(sets, fd)
