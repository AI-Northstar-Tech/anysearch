"""Core unit tests: routing, capability gating, response normalization, MCP."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest
import respx

from anysearch import AnySearch, Capability
from anysearch.exceptions import ProviderError, UnsupportedParameterError
from anysearch.providers import get_provider_class, list_provider_names
from anysearch.router import available_providers, enforce_capabilities, select_provider
from anysearch.types import SearchRequest


def test_all_providers_registered():
    names = list_provider_names()
    for required in ("octen", "exa", "parallel", "serpapi", "brave", "keiro"):
        assert required in names
    assert len(names) >= 19
    assert "gemini" in names


def test_aliases_resolve():
    assert get_provider_class("octen-ai").name == "octen"
    assert get_provider_class("serp").name == "serpapi"
    assert get_provider_class("ddg").name == "duckduckgo"
    assert get_provider_class("google").name == "google_pse"
    assert get_provider_class("keirolabs").name == "keiro"


def test_matrix_providers_and_python_sdk_providers_stay_in_parity():
    matrix_dir = Path(__file__).resolve().parents[2] / "docs/tools/search_matrix/data"
    slugs = {
        json.loads(path.read_text())["links"]["slug"]
        for path in matrix_dir.glob("*.json")
    }
    matrix_providers = {
        "serpapi" if slug.startswith("serpapi_") else slug
        for slug in slugs
    }
    assert matrix_providers == set(list_provider_names())


@respx.mock
def test_octen_search_sends_documented_filters_and_normalizes_response():
    route = respx.post("https://api.octen.ai/search").mock(
        return_value=httpx.Response(
            200,
            json={
                "code": 0,
                "msg": "success",
                "request_id": "octen-req-1",
                "data": {
                    "query": "fresh AI news",
                    "results": [
                        {
                            "title": "Octen result",
                            "url": "https://example.com/octen",
                            "highlight": "query-relevant excerpt",
                            "full_content": "# Full page",
                            "authors": "Example Author",
                            "time_published": "2026-07-27T12:00:00Z",
                        }
                    ],
                },
                "meta": {"latency": 62},
            },
        )
    )
    client = AnySearch(provider="octen", api_key="octen-test", env={})
    resp = client.search(
        "fresh AI news",
        max_results=7,
        search_type="news",
        language="EN",
        include_domains=["example.com"],
        start_published_date="2026-07-01T00:00:00Z",
        safe_search="moderate",
        include_content=True,
        highlights=True,
    )
    payload = json.loads(route.calls.last.request.content)
    assert route.calls.last.request.headers["x-api-key"] == "octen-test"
    assert payload["count"] == 7
    assert payload["topic"] == "news"
    assert payload["language"] == ["en"]
    assert payload["include_domains"] == ["example.com"]
    assert payload["time_basis"] == "published"
    assert payload["safesearch"] == "strict"
    assert payload["full_content"] == {"enable": True}
    assert resp.provider == "octen"
    assert resp.request_id == "octen-req-1"
    assert resp.latency_ms == 62
    assert resp.results[0].text == "# Full page"
    assert resp.results[0].highlights == ["query-relevant excerpt"]


def test_available_and_select_with_env():
    assert available_providers(env={}) == ["duckduckgo"]
    assert select_provider(env={}) == "duckduckgo"
    env = {"EXA_API_KEY": "x", "TAVILY_API_KEY": "y"}
    avail = available_providers(env=env)
    assert "exa" in avail and "tavily" in avail and "duckduckgo" in avail
    assert select_provider(env=env) == "exa"  # priority order
    assert select_provider(env={"ANYSEARCH_PROVIDER": "tavily", "EXA_API_KEY": "x"}) == "tavily"


def test_capability_enforcement_modes():
    serper = get_provider_class("serper")
    req = SearchRequest(query="q", include_domains=["a.com"], start_published_date="2024-01-01")
    with pytest.raises(UnsupportedParameterError):
        enforce_capabilities(serper, req, on_unsupported="error")
    # warn/ignore drop the unsupported fields
    safe = enforce_capabilities(serper, req, on_unsupported="ignore")
    assert safe.include_domains == []
    assert safe.start_published_date is None


def test_exa_supports_domains_and_content():
    exa = get_provider_class("exa")
    assert Capability.DOMAINS in exa.capabilities
    assert Capability.CONTENT in exa.capabilities


@respx.mock
def test_exa_search_normalizes_response():
    route = respx.post("https://api.exa.ai/search").mock(
        return_value=httpx.Response(
            200,
            json={
                "requestId": "req-1",
                "results": [
                    {
                        "title": "Vector DBs",
                        "url": "https://example.com/a",
                        "text": "full text here",
                        "summary": "a summary",
                        "highlights": ["hl one", "hl two"],
                        "score": 0.91,
                        "publishedDate": "2026-01-02",
                        "author": "Jane",
                    }
                ],
            },
        )
    )
    client = AnySearch(provider="exa", api_key="test-key", env={})
    resp = client.search("vector dbs", include_content=True, highlights=True, include_summary=True)

    assert route.called
    sent = route.calls.last.request
    assert sent.headers["x-api-key"] == "test-key"
    assert resp.provider == "exa"
    assert resp.request_id == "req-1"
    assert len(resp) == 1
    r = resp.results[0]
    assert r.title == "Vector DBs"
    assert r.url == "https://example.com/a"
    assert r.text == "full text here"
    assert r.summary == "a summary"
    assert r.highlights == ["hl one", "hl two"]
    assert r.source == "example.com"
    assert resp.urls == ["https://example.com/a"]


@respx.mock
def test_gemini_google_search_grounding():
    respx.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": "Spain won Euro 2024, defeating England 2-1 in the final."
                                }
                            ],
                            "role": "model",
                        },
                        "groundingMetadata": {
                            "webSearchQueries": ["UEFA Euro 2024 winner"],
                            "groundingChunks": [
                                {
                                    "web": {
                                        "uri": "https://example.com/uefa",
                                        "title": "uefa.com",
                                    }
                                },
                                {
                                    "web": {
                                        "uri": "https://example.com/news",
                                        "title": "aljazeera.com",
                                    }
                                },
                            ],
                        },
                    }
                ],
            },
        )
    )
    client = AnySearch(provider="gemini", api_key="gemini-test", env={})
    resp = client.search("Who won Euro 2024?", answer=True, max_results=5)
    assert resp.provider == "gemini"
    assert "Spain won Euro 2024" in (resp.answer or "")
    assert len(resp.results) == 2
    assert resp.results[0].url == "https://example.com/uefa"
    assert resp.results[0].title == "uefa.com"
    sent = respx.calls.last.request
    assert sent.headers["x-goog-api-key"] == "gemini-test"
    payload = json.loads(sent.read())
    assert payload["tools"] == [{"google_search": {}}]


@respx.mock
def test_tavily_answer_and_content():
    respx.post("https://api.tavily.com/search").mock(
        return_value=httpx.Response(
            200,
            json={
                "query": "q",
                "answer": "the answer",
                "results": [
                    {
                        "title": "T",
                        "url": "https://t.example/x",
                        "content": "snippet text",
                        "raw_content": "raw page text",
                        "score": 0.5,
                        "published_date": "2026-02-02",
                    }
                ],
            },
        )
    )
    client = AnySearch(provider="tavily", api_key="tvly-test", env={})
    resp = client.search("q", answer=True, include_content=True)
    assert resp.answer == "the answer"
    assert resp.results[0].text == "raw page text"
    assert resp.results[0].snippet == "snippet text"


@respx.mock
def test_keiro_search_sends_documented_body_auth_and_normalizes_results():
    route = respx.post("https://kierolabs.space/api/v2/keirolabs").mock(
        return_value=httpx.Response(
            200,
            json={
                "query": "keiro search",
                "total_results": 1,
                "request_id": "keiro-req-1",
                "results": [
                    {
                        "title": "Keiro source",
                        "url": "https://example.com/keiro",
                        "snippet": "source snippet",
                        "content": "source body",
                        "score": 0.82,
                        "published_date": "2026-06-01",
                    }
                ],
            },
        )
    )
    client = AnySearch(provider="keiro", api_key="keiro-test", env={})
    resp = client.search("keiro search", max_results=7)

    assert route.called
    sent = route.calls.last.request
    assert "authorization" not in sent.headers
    payload = json.loads(sent.read())
    assert payload["apiKey"] == "keiro-test"
    assert payload["query"] == "keiro search"
    assert payload["maxResults"] == 7
    assert resp.provider == "keiro"
    assert resp.request_id == "keiro-req-1"
    assert resp.total_results == 1
    assert resp.results[0].title == "Keiro source"
    assert resp.results[0].snippet == "source snippet"
    assert resp.results[0].source == "example.com"


@respx.mock
def test_keiro_content_mode_uses_content_endpoint_and_full_text():
    route = respx.post("https://kierolabs.space/api/v2/search/content").mock(
        return_value=httpx.Response(
            200,
            json={
                "results": [
                    {
                        "title": "Deep source",
                        "url": "https://example.com/deep",
                        "snippet": "deep snippet",
                        "full_text": "full page markdown",
                        "score": 0.91,
                    }
                ],
            },
        )
    )
    client = AnySearch(provider="keiro", api_key="keiro-test", env={})
    resp = client.search("keiro content", include_content=True, max_results=2, mode="deep")

    assert route.called
    sent = route.calls.last.request
    payload = json.loads(sent.read())
    assert payload["apiKey"] == "keiro-test"
    assert payload["query"] == "keiro content"
    assert payload["maxResults"] == 2
    assert payload["mode"] == "deep"
    assert resp.results[0].text == "full page markdown"


@respx.mock
def test_brave_get_request_and_parse():
    respx.get(url__startswith="https://api.search.brave.com/res/v1/web/search").mock(
        return_value=httpx.Response(
            200,
            json={
                "web": {
                    "results": [
                        {
                            "title": "B",
                            "url": "https://b.example",
                            "description": "desc",
                            "extra_snippets": ["x", "y"],
                            "page_age": "2026-03-03",
                        }
                    ]
                }
            },
        )
    )
    client = AnySearch(provider="brave", api_key="brave-test", env={})
    resp = client.search("q", highlights=True, max_results=5)
    assert resp.results[0].highlights == ["x", "y"]
    assert resp.results[0].published_date == "2026-03-03"


@respx.mock
def test_fallback_on_provider_error():
    respx.post("https://api.exa.ai/search").mock(return_value=httpx.Response(500, json={"error": "boom"}))
    respx.post("https://api.tavily.com/search").mock(
        return_value=httpx.Response(200, json={"results": [{"title": "ok", "url": "https://ok.example", "content": "c"}]})
    )
    client = AnySearch(
        provider="exa",
        api_key="exa-test",
        fallbacks=["tavily"],
        env={"TAVILY_API_KEY": "tvly-test"},
    )
    resp = client.search("q")
    assert resp.provider == "tavily"
    assert resp.results[0].title == "ok"


@respx.mock
def test_provider_error_raised_without_fallback():
    respx.post("https://api.exa.ai/search").mock(return_value=httpx.Response(401, json={"error": "bad key"}))
    client = AnySearch(provider="exa", api_key="bad", env={})
    with pytest.raises(ProviderError):
        client.search("q")


@respx.mock
async def test_async_search():
    respx.post("https://api.tavily.com/search").mock(
        return_value=httpx.Response(200, json={"results": [{"title": "A", "url": "https://a.example", "content": "c"}]})
    )
    client = AnySearch(provider="tavily", api_key="tvly-test", env={})
    resp = await client.asearch("q")
    assert resp.results[0].title == "A"


def test_unknown_kwargs_passthrough_to_extra():
    client = AnySearch(provider="exa", api_key="k", env={})
    req = client._build_request("exa", "q", {"use_autoprompt": True, "extra": {"foo": 1}})
    assert req.extra == {"foo": 1, "use_autoprompt": True}
