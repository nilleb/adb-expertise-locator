import uuid
import logging
from fastapi import FastAPI, Request
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Json
from typing import Optional, List
import json
from starlette.requests import Request
from starlette.responses import JSONResponse

from starlette_context import context, plugins
from starlette_context.middleware import RawContextMiddleware

from backends.es import search as es_search, document

from starlette_context.plugins.base import PluginUUIDBase


class SessionIDPlugin(PluginUUIDBase):
    key = "X-Session-ID"


logging.basicConfig(level=logging.INFO)
middleware = [
    Middleware(
        RawContextMiddleware,
        plugins=(plugins.RequestIdPlugin(), plugins.CorrelationIdPlugin(), SessionIDPlugin()),
    )
]

app = FastAPI(middleware=middleware)

origins = [
    "http://localhost.nilleb.com",
    "https://localhost.nilleb.com",
    "http://localhost",
    "http://localhost:8080",
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


@app.route("/")
async def index(request: Request):
    return JSONResponse(context.data)


def get_highlight(hit):
    highlights = hit.get("highlight", {})
    return " ".join(value for value_list in highlights.values() for value in value_list)


def prepare_response(query, res):
    response = {
        "query": query,
        "total": res["hits"]["total"]["value"],
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
    result = {
        "uid": uid,
        "score": hit.get("_score"),
        "title": hit["_source"].get("author", "unknown"),
        "highlight": get_highlight(hit),
        "source": json.dumps(hit["_source"]),
        "kind": hit["_source"].get("kind", "author"),
        "urn": f"elasticsearch://{url}",
    }
    return result
