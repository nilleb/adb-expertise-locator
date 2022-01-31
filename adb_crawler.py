# extract links to from adb.org public data repository search engine and project pages
# https://www.adb.org/projects/documents/rss?terms=report%20and%20recommendation%20to%20the%20president&sort_by=field_date_content&sort_order=ASC&page=121
# https://www.adb.org/projects/documents?terms=recommendation%20to%20the%20president&page=122

import json

import logging
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

QUERIES = {
    "reports": "recommendation%20to%20the%20president",
}


def complete_url(url):
    return url if "www.adb.org" in url else f"https://www.adb.org{url}"


def visit_page(query, page_number):
    """Yield the projects on the page."""
    url = f"https://www.adb.org/projects/documents?terms={query}&page={page_number}"
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, "html.parser")
    divs = soup.find_all("div", class_="item-title")
    for div in divs:
        yield complete_url(list(div.children)[0]["href"])


def visit_project(url):
    """Yields the list of downloadable files for the project."""
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, "html.parser")
    links = []
    for anchor in soup.find_all("a"):
        href = anchor.get("href")
        if href.endswith(".pdf"):
            links.append(href)
            yield complete_url(href)
    if not links:
        logging.warning(f"no link found for project: {url}")


def public_search(kind):
    """Use the ADB public search engine to return all the documents matching a certain query."""
    urls = []
    pages_count = 137

    query = QUERIES[kind]
    for page in range(1, pages_count):
        urls.extend(visit_page(query, page))

    urls_set = set(urls)
    with open("data/intermediate/project_urls.json", "w") as fd:
        data = {kind: list(urls_set)}
        json.dump(data, fd)

    logging.info(
        f"{kind}: visited {pages_count} pages, {len(urls_set)} unique projects found"
    )
    return urls_set


def generate_links(kind):
    """Orchestrate the search functionality and the pdf link extraction from the project page."""
    try:
        with open("data/intermediate/project_urls.json") as fd:
            data = json.load(fd)
        urls_set = set(data[kind])
    except:
        urls_set = public_search(kind)

    try:
        with open("data/intermediate/pdfs.json") as fd:
            pdfs = json.load(fd)
    except:
        pdfs = []

    try:
        with open("data/intermediate/visited_projects.json") as fd:
            visited_set = set(json.load(fd))
    except:
        visited_set = set()

    for url in urls_set:
        if url in visited_set:
            continue
        logging.info(f"{len(urls_set)-len(visited_set)} to go!")

        pdfs.extend(visit_project(url))
        with open("data/intermediate/pdfs.json", "w") as fd:
            json.dump(pdfs, fd)

        visited_set.add(url)
        with open("data/intermediate/visited_projects.json", "w") as fd:
            json.dump(list(visited_set), fd)

    pdfs = list(set(pdfs))
    logging.info(f"{kind}: extracted {len(pdfs)} unique pdf urls")

    return pdfs


def crawl():
    sets = {}
    for kind in QUERIES.keys():
        urls = generate_links(kind)
        sets = {kind: urls}
    return sets


def cached_crawl():
    try:
        with open("data/intermediate/sets.json") as fd:
            sets = json.load(fd)
    except:
        sets = crawl()
        with open("data/intermediate/sets.json", "w") as fd:
            json.dump(sets, fd)
    return sets


def describe(sets):
    with open("data/intermediate/project_urls.json") as fd:
        data = json.load(fd)
    for key, value in data.items():
        logging.info(f"{key} => {len(value)} projects to analyze")
    for key, value in sets.items():
        logging.info(f"{key} => {len(value)} documents to download")
        logging.info(f"{key} => {len([url for url in value if 'rrp' in url])} rrp documents to download")


if __name__ == "__main__":
    sets = cached_crawl()
    describe(sets)
