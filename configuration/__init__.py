import os
import yaml
import re
import json
import logging

cwd = os.path.dirname(os.path.abspath(__file__))
configuration_file = f"{cwd}/configuration.yml"
with open(configuration_file) as fd:
    configuration = yaml.load(fd, Loader=yaml.FullLoader)


DEFAULT_SEARCH_ENGINE = configuration.get("search_engine", {}).get("name")
ENVIRONMENT_ES_SERVER_ADDRESS = os.environ.get("ELASTICSEARCH_URL")
CONFIGURATION_ES_SERVER_ADDRESS = configuration["search_engines"][
    DEFAULT_SEARCH_ENGINE
]["url"]
USE_ENVIRONMENT_VARIABLE_AS = configuration.get("search_engine", {}).get(
    "use_environment_variable_as", "none"
)

ES_SERVER_ADDRESS = {
    "fallback": CONFIGURATION_ES_SERVER_ADDRESS or ENVIRONMENT_ES_SERVER_ADDRESS,
    "default": ENVIRONMENT_ES_SERVER_ADDRESS or CONFIGURATION_ES_SERVER_ADDRESS,
    "none": CONFIGURATION_ES_SERVER_ADDRESS,
}.get(USE_ENVIRONMENT_VARIABLE_AS)


ORGANIZATION_ID = configuration.get("organization_id")
ES_INDEX_NAME = index = configuration.get("index_format").format(
    organization_id=ORGANIZATION_ID
)
ES_QUERY_TEMPLATE_PATH = f"{cwd}/query.json"
LIMIT = 100000

linkedin_default = configuration.get("linkedin", {}).get("default", {})
LINKEDIN_EMAIL = linkedin_default.get("email", "sample@linkedin.com")
LINKEDIN_PASSWORD = linkedin_default.get("password", "password")


CONFIGURED_FACETS = configuration.get("faceted search")


def camel_case_to_spaces(label):
    return re.sub(r"((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))", r" \1", label).lower()


def spaces_to_camel_case(label):
    field = "".join(x for x in label.title() if not x.isspace())
    return field[:1].lower() + field[1:]


def aggregations():
    aggs = {
        f"{camel_case_to_spaces(field)}s": {"terms": {"field": f"{field}.keyword"}}
        for field in CONFIGURED_FACETS
    }

    return aggs


def facets_to_query(facets):
    must_array = []
    for facet in facets:
        field = spaces_to_camel_case(facet.get("name")).rstrip("s")
        must_array.append({"terms": {f"{field}.keyword": facet.get("values", [])}})

    return must_array


def compose_query(query_string, facets):
    with open(ES_QUERY_TEMPLATE_PATH) as template_fd:
        template = template_fd.read()
    template = template.replace("{{query_string}}", query_string)
    body = json.loads(template)
    must = facets_to_query(facets)
    if must:
        body["query"]["bool"]["must"] = must
    body["aggs"] = aggregations()
    logging.info(json.dumps(body))
    return body


DEFAULT_INDEX_SETTINGS_FILE = f"{cwd}/index_settings.json"
with open(DEFAULT_INDEX_SETTINGS_FILE) as fd:
    DEFAULT_INDEX_SETTINGS = fd.read()
