"""Keiro — source-cited web search via the v2 API."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

import httpx

from .._http import PreparedRequest
from ..types import SearchRequest, SearchResponse
from .base import BaseProvider, Capability

_MODE = {"fast": "light", "balanced": "ai", "deep": "deep"}


def _first_string(*values: Any) -> Optional[str]:
    for value in values:
        if isinstance(value, str) and value:
            return value
    return None


def _source_items(data: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    if isinstance(data.get("results"), list):
        return data["results"]
    if isinstance(data.get("sources"), list):
        return data["sources"]
    if isinstance(data.get("citations"), list):
        return data["citations"]
    answer = data.get("answer")
    if isinstance(answer, dict) and isinstance(answer.get("sources"), list):
        return answer["sources"]
    nested = data.get("data")
    if isinstance(nested, dict):
        if isinstance(nested.get("results"), list):
            return nested["results"]
        if isinstance(nested.get("sources"), list):
            return nested["sources"]
    return []


def _answer_text(data: Dict[str, Any]) -> Optional[str]:
    answer = data.get("answer")
    if isinstance(answer, str):
        return answer
    if isinstance(answer, dict):
        return _first_string(answer.get("text"), answer.get("content"))
    nested = data.get("data")
    if isinstance(nested, dict):
        return _first_string(nested.get("answer"))
    return None


def _endpoint_for(req: SearchRequest) -> str:
    if req.include_content:
        return "/api/v2/search/content"
    if req.mode:
        return "/api/v2/search/fast"
    return "/api/v2/keirolabs"


class KeiroProvider(BaseProvider):
    name = "keiro"
    env_keys = ("KEIRO_API_KEY",)
    base_url_env = ("KEIRO_BASE_URL",)
    default_base_url = "https://kierolabs.space"
    capabilities = frozenset(
        {
            Capability.MODE,
            Capability.CONTENT,
        }
    )

    def prepare(self, req: SearchRequest) -> PreparedRequest:
        endpoint = _endpoint_for(req)
        body: Dict[str, Any] = {
            "apiKey": self.api_key,
            "query": req.query,
            "maxResults": req.max_results,
        }
        if endpoint != "/api/v2/keirolabs":
            body["mode"] = _MODE.get(req.mode or "", "ai")
        body.update(req.extra)
        return PreparedRequest(
            method="POST",
            url=f"{self.base_url}{endpoint}",
            headers={"Content-Type": "application/json"},
            json=body,
        )

    def parse(self, response: httpx.Response, req: SearchRequest, elapsed_ms: float) -> SearchResponse:
        data = response.json()
        results = []
        for item in _source_items(data):
            snippet = _first_string(
                item.get("snippet"),
                item.get("description"),
                item.get("content"),
                item.get("text"),
            )
            results.append(
                self._result(
                    title=_first_string(item.get("title"), item.get("name")),
                    url=_first_string(item.get("url"), item.get("link"), item.get("source_url")),
                    snippet=snippet,
                    text=_first_string(
                        item.get("full_text"), item.get("text"), item.get("content"), item.get("raw_content")
                    )
                    if req.include_content
                    else None,
                    score=item.get("score") if isinstance(item.get("score"), (int, float)) else None,
                    published_date=_first_string(
                        item.get("published_date"), item.get("publishedDate"), item.get("date")
                    ),
                    raw=item,
                )
            )
        return self._response(
            req,
            results,
            data,
            answer=_answer_text(data),
            total_results=data.get("total_results") or data.get("totalResults"),
            request_id=_first_string(data.get("request_id"), data.get("requestId"), data.get("id")),
            elapsed_ms=elapsed_ms,
        )
