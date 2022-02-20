from datetime import datetime
import hashlib
import json
import logging
import os
import uuid
import secrets
from typing import List, Optional

from fastapi import Depends, FastAPI, Request
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Json
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse
from starlette_context import context, plugins
from starlette_context.middleware import RawContextMiddleware
from starlette_context.plugins.base import PluginUUIDBase
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from backends.es import create_indexer, document
from backends.es import search as es_search
from common.filters import should_exclude_keyword
from common.io import read_object

try:
    FACES_URLS = read_object("data/faces/all_faces_urls.json")
except:
    FACES_URLS = []

try:
    REPORTS_DATA = read_object("data/intermediate/documents.json")
except:
    REPORTS_DATA = {}

ROLES = [
    "Economist" "Senior economist",
    "Principal economist",
    "Director",
    "Transport specialist",
    "Senior Transport specialist",
    "Principal Transport specialist",
    "Safeguard specialist",
    "Senior Safeguard specialist",
    "Principal Safeguard specialist",
    "Human resources specialist",
    "Senior Human resources specialist",
    "Principal Human resources specialist",
    "Energy specialist",
    "Senior Energy specialist",
    "Principal Energy specialist",
]

ORGANIZATIONS = [
    "SERD",
    "SARD",
    "CWRD",
    "EARD",
    "PSOD",
    "PARD",
    "SDCC",
    "Office of the General Counsel",
    "RSDD",
    "ERCD",
]

security = HTTPBasic()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "stanleyjobson")
    correct_password = secrets.compare_digest(credentials.password, "swordfish")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


class SessionIDPlugin(PluginUUIDBase):
    key = "X-Session-ID"


logging.basicConfig(level=logging.INFO)
middleware = [
    Middleware(
        RawContextMiddleware,
        plugins=(
            plugins.RequestIdPlugin(),
            plugins.CorrelationIdPlugin(),
            SessionIDPlugin(),
        ),
    )
]

app = FastAPI(middleware=middleware)

origins = [
    "http://localhost.nilleb.com",
    "https://localhost.nilleb.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Session-ID"] = request.headers.get(
        "X-Session-ID", str(uuid.uuid4())
    )
    return response


class SearchQueryFacet(BaseModel):
    name: str
    values: List[str]


class SearchQuery(BaseModel):
    query: str
    facets: Optional[List[SearchQueryFacet]]


class SearchResult(BaseModel):
    uid: str
    title: str
    highlight: Optional[str]
    previewImage: Optional[str]
    kind: Optional[str]
    source: Optional[Json]
    score: float
    urn: str
    api_url: str


class SearchBucket(BaseModel):
    key: str
    doc_count: int


class SearchFacet(BaseModel):
    name: str
    buckets: List[SearchBucket]


class SearchResponse(BaseModel):
    query: str
    results: Optional[List[SearchResult]]
    suggestions: Optional[List[str]]
    total: int
    facets: Optional[List[SearchFacet]]


class SignalRequest(BaseModel):
    verb: str
    uid: str
    query: Optional[str]
    description: Optional[str]


@app.get("/api/v1/document/{uid}")
async def get_document(uid: str) -> SearchResult:
    res = document(uid)
    return prepare_result(res)


def _signal(verb, query, document_uid, description):
    session_id = context.data.get("X-Session-ID", str(uuid.uuid4()))
    uid = context.data.get("X-Request-ID", str(uuid.uuid4()))
    document = {"id": uid, "session_id": session_id}
    document["verb"] = verb
    document["query"] = query
    document["document_uid"] = document_uid
    document["description"] = description
    document["timestamp"] = datetime.utcnow()
    indexer = create_indexer("signal")
    indexer.setup_index()
    indexer.index_single_document(document)


@app.post("/api/v1/signal")
async def signal(payload: SignalRequest) -> None:
    signalling = dict(payload.dict())
    _signal(
        signalling["verb"],
        signalling.get("query", ""),
        signalling.get("uid", ""),
        signalling.get("description", ""),
    )
    track("signal", signalling, None)


def track(path, params, response):
    logging.info(f"- {context.data} {path} ({params}) -> {response}")


@app.post("/api/v1/search")
async def search(payload: SearchQuery) -> SearchResponse:
    facets = payload.dict().get("facets")
    res = es_search(payload.query, facets)
    _signal("search", payload.query, None, None)
    track("search", payload.query, res)
    return prepare_response(payload.query, res)


@app.route("/context")
async def index(request: Request):
    return JSONResponse(context.data)


def get_highlight(hit):
    highlights = hit.get("highlight", {})
    return " ".join(value for value_list in highlights.values() for value in value_list)


def prepare_response(query, res):
    total = res["hits"]["total"]
    total = total.get("value") if isinstance(total, dict) else total
    response = {
        "query": query,
        "total": total,
    }
    suggestions = set()
    for suggestion in res["suggest"]["suggest-1"]:
        for opt in suggestion["options"]:
            suggestions.add(opt.get("text"))

    response["suggestions"] = []
    if suggestions:
        response["suggestions"] = list(suggestions)

    response["results"] = []

    for hit in res["hits"]["hits"]:
        result = prepare_result(hit)
        result["api_url"] = f'api/v1/document/{hit.get("_id")}'
        response["results"].append(result)

    response["facets"] = []
    for name, facet in res.get("aggregations", {}).items():
        buckets = [bucket for bucket in facet.get("buckets", [])]
        facet_object = {"name": name, "buckets": buckets}
        response["facets"].append(facet_object)

    return SearchResponse(**response)


def prepare_result(hit):
    uid = hit.get("_id", str(uuid.uuid4()))
    url = f'{hit.get("_index")}/_doc/{hit.get("_id")}'
    source = prepare_source(uid, hit["_source"])
    result = {
        "uid": uid,
        "score": hit.get("_score"),
        "title": hit["_source"].get("fullname", "unknown"),
        "highlight": get_highlight(hit),
        "source": json.dumps(source),
        "kind": hit["_source"].get("kind", "author"),
        "urn": f"elasticsearch://{url}",
        "previewImage": previewImage(uid, hit["_source"]),
    }
    return result


def previewImage(uid, source):
    if uid == "jules-hugot":
        return "https://pbs.twimg.com/profile_images/1064197342490898432/y8VRDD-o_400x400.jpg"
    if uid == "dmitry-kabrelyan":
        return "https://dgalywyr863hv.cloudfront.net/pictures/athletes/811928/179461/6/large.jpg"
    profile_picture = source.get("profilePicture")
    if profile_picture:
        return profile_picture
    return pseudo_random_choice(uid, FACES_URLS)


def uid_to_number(uid):
    encoded = hashlib.md5(uid.encode("utf-8")).hexdigest()
    return int(encoded[6:12], 16)


def pseudo_random_choice(uid, array):
    number = uid_to_number(uid)
    return f"{array[number % len(array)]} (🎲)"


def random_role(uid):
    return pseudo_random_choice(uid, ROLES)


def random_organization(uid):
    return pseudo_random_choice(uid, ORGANIZATIONS)


def prepare_source(uid, source):
    if not source.get("telephoneNumber"):
        number = uid_to_number(uid)
        source["telephoneNumber"] = f"555-{number}"
    if not source.get("email"):
        source["email"] = f"{uid}@adb.nilleb.com"

    if not source.get("role"):
        source["role"] = random_role(uid)
    elif isinstance(source["role"], list):
        source["role"] = source["role"][0]

    if not source.get("organization"):
        source["organization"] = random_organization(uid)
    elif isinstance(source["organization"], list):
        source["organization"] = source["organization"][0]

    source["documents"] = prepare_documents(source.get("links", []))

    source["keywords"] = [
        keyword
        for keyword in source.get("keywords", [])
        if not should_exclude_keyword(keyword)
    ]

    return source


def prepare_documents(documents):
    filenames = [os.path.basename(document) for document in documents]
    filenames = list(set(filenames))

    def get_report_info(filename):
        return REPORTS_DATA.get(filename, {})

    return [get_report_info(filename) for filename in filenames]


@app.route("/")
async def index(request: Request):
    return FileResponse("ui/dist/index.html")


@app.route("/view")
async def index(request: Request):
    return FileResponse("ui/dist/index.html")


app.mount("/", StaticFiles(directory="ui/dist"), name="dist")
