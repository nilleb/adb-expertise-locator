import requests
import logging
from elasticsearch import Elasticsearch

from configuration import (
    ES_INDEX_NAME,
    ES_SERVER_ADDRESS,
    DEFAULT_INDEX_SETTINGS,
    compose_query,
)


class ElasticSearchIndexer(object):
    def __init__(self, server_address, index_name, index_settings) -> None:
        super().__init__()
        self.server_address = server_address
        self.index_name = index_name
        self.index_settings = index_settings

    def setup_index(self):
        index_uri = f"{self.server_address}/{self.index_name}"
        response = requests.put(
            index_uri,
            json=self.index_settings,
            headers={"content-type": "application/json"},
        )
        logging.info(response)
        if not response.ok:
            rd = response.json()
            if rd.get("error", {}).get("type") == "resource_already_exists_exception":
                return
            logging.warning(rd)
        response.raise_for_status()

    def index_single_document(self, document):
        doc_id = document.get("id")
        doc_uri = f"{self.server_address}/{self.index_name}/_doc/{doc_id}"
        doc_size = sum(
            [
                len(value)
                if isinstance(value, str)
                else sum([len(sub) for sub in value])
                for value in document.values()
            ]
        )
        logging.info(f"{doc_id}, {doc_size}")
        response = requests.put(
            doc_uri, json=document, headers={"content-type": "application/json"}
        )
        logging.info(response)


def create_indexer():
    return ElasticSearchIndexer(
        ES_SERVER_ADDRESS, ES_INDEX_NAME, DEFAULT_INDEX_SETTINGS
    )


def search(query):
    es = Elasticsearch([ES_SERVER_ADDRESS])
    body = compose_query(query)
    return es.search(
        index=ES_INDEX_NAME,
        **body,
    )


def document(uid):
    es = Elasticsearch([ES_SERVER_ADDRESS])
    return es.get(
        id=uid,
        index=ES_INDEX_NAME,
    )
