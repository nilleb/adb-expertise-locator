import ssl
import logging
from elasticsearch import Elasticsearch, TransportError
from elasticsearch.exceptions import RequestError
from elasticsearch.connection import create_ssl_context
from elasticsearch_dsl import Search

from configuration import (
    ES_INDEX_NAME,
    ES_SERVER_ADDRESS,
    DEFAULT_INDEX_SETTINGS,
    compose_autocomplete,
    compose_query,
)


def create_es_connection():
    context = create_ssl_context(cafile="configuration/ca.pem")
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return Elasticsearch([ES_SERVER_ADDRESS], ssl_context=context, timeout=60)


class IndexingException(Exception):
    def __init__(self, exception, *args: object) -> None:
        self.inner_exception = exception
        super().__init__(*args)


class ElasticSearchIndexer(object):
    def __init__(self, server_address, index_name, index_settings) -> None:
        super().__init__()
        self.server_address = server_address
        self.index_name = index_name
        self.index_settings = index_settings

    def setup_index(self):
        es = create_es_connection()
        try:
            es.indices.create(index=self.index_name, body=self.index_settings)
        except RequestError as re:
            if re.error != "resource_already_exists_exception":
                raise

    def document_exists(self, doc_id):
        es = create_es_connection()
        try:
            return es.exists(self.index_name, doc_id)
        except TransportError:
            return False

    def all_document_ids(self):
        # heap insufficient with 2G of ram
        es = create_es_connection()
        s = Search(using=es, index=self.index_name)
        s.source([])
        return [h.meta.id for h in s.scan()]

    def index_single_document(self, document):
        doc_id = document.get("id")
        doc_uri = f"{self.server_address}/{self.index_name}/_doc/{doc_id}"
        es = create_es_connection()
        try:
            es.index(index=self.index_name, document=document, id=doc_id)
        except Exception as ex:
            logging.exception(doc_uri)
            raise IndexingException(ex)

    def update_document(self, uid, **kwargs):
        es = create_es_connection()
        try:
            return es.update(index=self.index_name, doc_type="_doc", id=uid, doc=kwargs)
        except Exception as ex:
            logging.exception(uid)
            raise IndexingException(ex)


def create_indexer(index=None):
    if not index:
        index = ES_INDEX_NAME

    return ElasticSearchIndexer(ES_SERVER_ADDRESS, index, DEFAULT_INDEX_SETTINGS)


def search(query, facets):
    es = create_es_connection()
    body = compose_query(query, facets)
    return es.search(
        index=ES_INDEX_NAME,
        **body,
    )


def complete(prefix):
    es = create_es_connection()
    body = compose_autocomplete(prefix)
    return es.search(
        index=ES_INDEX_NAME,
        **body,
    )


def document(uid):
    es = create_es_connection()
    return es.get(
        id=uid,
        index=ES_INDEX_NAME,
    )
