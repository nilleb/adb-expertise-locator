# extract links to from adb.org public data repository search engine and project pages
# https://www.adb.org/projects/documents/rss?terms=report%20and%20recommendation%20to%20the%20president&sort_by=field_date_content&sort_order=ASC&page=121
# https://www.adb.org/projects/documents?terms=recommendation%20to%20the%20president&page=122

import logging
import os
import sys
import requests
from bs4 import BeautifulSoup

from common.filters import should_be_downloaded
from common.constants import SETS_FILEPATH, PROJECT_URLS_FILEPATH
from common.io import read_object, safe_read_object, write_object

logging.basicConfig(level=logging.INFO)


QUERIES = {
    "reports": {
        "url": "https://www.adb.org/projects/documents?terms=recommendation%20to%20the%20president&page={page_number}",
        "pages_count": 137,
    },
    "ta": {
        "url": "https://www.adb.org/projects/documents/doctype/Technical%20Assistance%20Reports?page={page_number}",
        "pages_count": 590,
    },
}


def complete_url(url):
    return url if "www.adb.org" in url else f"https://www.adb.org{url}"


def visit_page(url, page_number):
    """Yield the projects on the page."""
    html_text = requests.get(url.format(page_number=page_number)).text
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

    info = QUERIES[kind]
    url = info.get("url")
    pages_count = info.get("pages_count")
    for page in range(1, pages_count):
        logging.info(
            f"{kind}: page {page} ({len(urls)} project urls discovered so far)"
        )
        urls.extend(visit_page(url, page))

    urls_set = set(urls)
    data = safe_read_object(PROJECT_URLS_FILEPATH, {})
    data[kind] = list(urls_set)
    write_object(data, PROJECT_URLS_FILEPATH)

    logging.info(
        f"{kind}: visited {pages_count} pages, {len(urls_set)} unique projects found"
    )

    return urls_set


def generate_links(kind):
    """Orchestrate the search functionality and the pdf link extraction from the project page."""
    try:
        data = read_object(PROJECT_URLS_FILEPATH)
        urls_set = set(data[kind])
    except:
        urls_set = public_search(kind)

    pdfs_path = f"data/intermediate/pdfs_{kind}.json"
    projects_path = f"data/intermediate/visited_projects_{kind}.json"
    pdfs = safe_read_object(pdfs_path, [])
    visited_set = set(safe_read_object(projects_path, []))

    for url in urls_set:
        if url in visited_set:
            continue
        logging.info(f"{len(urls_set)-len(visited_set)} projects to go!")

        pdfs.extend(visit_project(url))
        write_object(pdfs, pdfs_path)

        visited_set.add(url)
        write_object(list(visited_set), projects_path)

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
        sets = read_object(SETS_FILEPATH)
    except:
        sets = crawl()
        write_object(sets, SETS_FILEPATH)
    return sets


def describe(sets):
    data = read_object(PROJECT_URLS_FILEPATH)
    for key, value in data.items():
        logging.info(f"{key} => {len(value)} projects to analyze")
    for key, value in sets.items():
        logging.info(f"{key} => {len(value)} documents to download")
        logging.info(
            f"{key} => {len([url for url in value if should_be_downloaded(url)])} documents to download"
        )


if __name__ == "__main__":
    if sys.argv[-1] == "reset":
        os.unlink(SETS_FILEPATH)
        os.unlink(PROJECT_URLS_FILEPATH)
    sets = cached_crawl()
    describe(sets)
