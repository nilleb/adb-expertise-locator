import hashlib
import json
import logging
import os
import uuid
import secrets
from typing import List, Optional

from fastapi import FastAPI, Request
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Json
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse
from starlette_context import context, plugins
from starlette_context.middleware import RawContextMiddleware
from starlette_context.plugins.base import PluginUUIDBase
from fastapi.staticfiles import StaticFiles

from backends.es import document
from backends.es import search as es_search


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


class SearchQuery(BaseModel):
    query: str


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


class SearchResponse(BaseModel):
    query: str
    results: Optional[List[SearchResult]]
    suggestions: Optional[List[str]]
    total: int


class SignalRequest(BaseModel):
    verb: str
    uid: str
    query: Optional[str]
    description: Optional[str]


@app.get("/api/v1/document/{uid}")
async def get_document(uid: str) -> SearchResult:
    res = document(uid)
    return prepare_result(res)


@app.post("/api/v1/signal")
async def signal(payload: SignalRequest) -> None:
    track("signal", payload.dict(), None)


def track(path, params, response):
    logging.info(f"- {context.data} {path} ({params}) -> {response}")


@app.post("/api/v1/search")
async def search(payload: SearchQuery) -> SearchResponse:
    res = es_search(payload.query)
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
    }
    return result


def prepare_source(uid, source):
    if not source.get("telephoneNumber"):
        encoded = hashlib.md5(uid.encode("utf-8")).hexdigest()
        number = int(encoded[6:12], 16)
        source["telephoneNumber"] = f"555-{number}"
    if not source.get("email"):
        source["email"] = f"{uid}@adb.nilleb.com"
    source["documents"] = prepare_documents(source.get("links", []))
    print(source)
    return source


def load_report_names():
    with open("data/intermediate/sets.json") as fd:
        sets = json.load(fd)
    return {os.path.basename(path): path for path in sets.get("reports")}


REPORT_NAMES = load_report_names()


def prepare_documents(documents):
    filenames = [os.path.basename(document) for document in documents]
    filenames = list(set(filenames))

    def short_id(filename):
        return filename.split("-")[0]

    def get_report(filename):
        return REPORT_NAMES.get(
            filename,
            f"https://www.adb.org/sites/default/files/project-documents/{short_id(filename)}/{filename}",
        )

    return [get_report(filename) for filename in filenames]


@app.route("/")
async def index(request: Request):
    return FileResponse("ui/dist/index.html")


@app.route("/view")
async def index(request: Request):
    return FileResponse("ui/dist/index.html")


app.mount("/", StaticFiles(directory="ui/dist"), name="dist")
