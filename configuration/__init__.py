import os
import yaml
import json
import logging

cwd = os.path.dirname(os.path.abspath(__file__))
configuration_file = f"{cwd}/configuration.yml"
with open(configuration_file) as fd:
    configuration = yaml.load(fd, Loader=yaml.FullLoader)


DEFAULT_SEARCH_ENGINE = configuration["search_engine"]
ES_SERVER_ADDRESS = os.environ.get(
    "ELASTICSEARCH_URL", configuration["search_engines"][DEFAULT_SEARCH_ENGINE]["url"]
)
ORGANIZATION_ID = configuration.get("organization_id")
ES_INDEX_NAME = index = configuration.get("index_format").format(
    organization_id=ORGANIZATION_ID
)
ES_QUERY_TEMPLATE_PATH = f"{cwd}/query.json"
LIMIT = 100000


def compose_query(query_string):
    with open(ES_QUERY_TEMPLATE_PATH) as template_fd:
        template = template_fd.read()
    template = template.replace("{{query_string}}", query_string)
    body = json.loads(template)
    logging.info(body)
    return body


DEFAULT_INDEX_SETTINGS_FILE = f"{cwd}/index_settings.json"
with open(DEFAULT_INDEX_SETTINGS_FILE) as fd:
    DEFAULT_INDEX_SETTINGS = fd.read()
