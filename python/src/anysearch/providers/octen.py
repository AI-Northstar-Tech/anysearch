"""Octen AI — low-latency web search with filters, highlights, and full content."""

from __future__ import annotations

import httpx

from .._http import PreparedRequest
from ..types import SearchRequest, SearchResponse
from .base import BaseProvider, Capability


class OctenProvider(BaseProvider):
    name = "octen"
    aliases = ("octen_ai",)
    env_keys = ("OCTEN_API_KEY",)
    default_base_url = "https://api.octen.ai"
    extra_package = "octen"
    native_client = ("octen", ("Octen",))
    capabilities = frozenset(
        {
            Capability.DOMAINS,
            Capability.LANGUAGE,
            Capability.DATE,
            Capability.SAFE_SEARCH,
            Capability.CONTENT,
            Capability.HIGHLIGHTS,
            Capability.NEWS,
        }
    )

    def prepare(self, req: SearchRequest) -> PreparedRequest:
        body = {
            "query": req.query,
            "count": req.max_results,
            "topic": "news" if req.search_type == "news" else "general",
        }
        if req.include_domains:
            body["include_domains"] = req.include_domains
        if req.exclude_domains:
            body["exclude_domains"] = req.exclude_domains
        if req.language:
            body["language"] = [req.language.lower()]
        if req.start_published_date or req.end_published_date:
            body["time_basis"] = "published"
        if req.start_published_date:
            body["start_time"] = req.start_published_date
        if req.end_published_date:
            body["end_time"] = req.end_published_date
        if req.safe_search:
            body["safesearch"] = "off" if req.safe_search == "off" else "strict"
        if req.highlights:
            body["highlight"] = {"enable": True}
        if req.include_content:
            body["full_content"] = {"enable": True}
        body.update(req.extra)
        return PreparedRequest(
            method="POST",
            url=f"{self.base_url}/search",
            headers={"x-api-key": self.api_key, "Content-Type": "application/json"},
            json=body,
        )

    def parse(self, response: httpx.Response, req: SearchRequest, elapsed_ms: float) -> SearchResponse:
        payload = response.json()
        data = payload.get("data") or {}
        results = []
        for item in data.get("results", []) or []:
            highlight = item.get("highlight")
            results.append(
                self._result(
                    title=item.get("title"),
                    url=item.get("url"),
                    snippet=highlight,
                    text=item.get("full_content"),
                    highlights=[highlight] if highlight else [],
                    published_date=item.get("time_published"),
                    author=item.get("authors"),
                    raw=item,
                )
            )
        provider_latency = (payload.get("meta") or {}).get("latency")
        return self._response(
            req,
            results,
            payload,
            request_id=payload.get("request_id"),
            elapsed_ms=provider_latency if isinstance(provider_latency, (int, float)) else elapsed_ms,
        )
