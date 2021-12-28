import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Json
from typing import Optional, List
import json
from backends.es import search as es_search

app = FastAPI()

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
    url: str


class SearchResponse(BaseModel):
    query: str
    results: Optional[List[SearchResult]]
    suggestions: Optional[List[str]]
    total: int


@app.post("/api/v1/search")
async def search(payload: SearchQuery) -> SearchResponse:
    res = es_search(payload.query)
    return prepare_response(payload.query, res)


def get_highlight(hit):
    title_highlight = hit.get("highlight", {}).get("title")
    description_highlight = hit.get("highlight", {}).get("description")
    if isinstance(title_highlight, list):
        title_highlight = "".join(title_highlight)
    if isinstance(description_highlight, list):
        description_highlight = "".join(description_highlight)
    highlight = ""
    if title_highlight:
        highlight += title_highlight
    if description_highlight:
        highlight += description_highlight
    return highlight


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
        result = {
            "uid": hit["_source"]["identifier"],
            "score": hit["_score"],
            "title": hit["_source"].get("title", "unknown"),
            "highlight": get_highlight(hit),
            "source": json.dumps(hit["_source"]),
            "kind": hit["_source"].get("kind", "linear"),
        }
        response["results"].append(result)

    logging.info(json.dumps(response))

    return SearchResponse(**response)
