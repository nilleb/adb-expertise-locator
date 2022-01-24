import logging
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError

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
        es = Elasticsearch([ES_SERVER_ADDRESS])
        try:
            es.indices.create(index=self.index_name, body=self.index_settings)
        except RequestError as re:
            if re.error != 'resource_already_exists_exception':
                raise

    def index_single_document(self, document):
        doc_id = document.get("id")
        doc_uri = f"{self.server_address}/{self.index_name}/_doc/{doc_id}"
        es = Elasticsearch([ES_SERVER_ADDRESS], timeout=600)
        try:
            es.index(index=self.index_name, document=document, id=doc_id)
        except:
            logging.exception(doc_uri)


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
