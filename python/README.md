# anysearch (Python)

**One interface for every web search API.** `anysearch` is an adapter layer — think
LiteLLM, but for search providers — that lets you call Exa, Parallel, Brave, Tavily,
SerpAPI, Perplexity, Linkup, Firecrawl, and more through a single function with a
common set of parameters and a common response shape. It also ships a dependency-free
**stdio MCP server** and optional **FastAPI proxy server** that adapt to whatever API
keys you have configured.

```python
import anysearch

# Auto-selects a provider based on which API keys are set in your environment.
resp = anysearch.search("best vector databases 2026", max_results=5)
for r in resp:
    print(r.title, r.url)

# Pin a provider and ask for richer content — same parameters everywhere.
resp = anysearch.search(
    "how do transformers work",
    provider="exa",
    include_content=True,
    highlights=True,
    include_summary=True,
)
```

## Install

Install the latest version from GitHub **`main`** (not on PyPI yet):

```bash
pip install "git+https://github.com/dhruv-anand-aintech/anysearch.git@main#subdirectory=python"
# or
uv add "anysearch-sdk @ git+https://github.com/dhruv-anand-aintech/anysearch.git@main#subdirectory=python"
```

The base install works for **all** providers (every adapter is REST-based on `httpx`).
Use extras to also install a provider's official SDK (for `anysearch.native(...)`):

```bash
pip install "anysearch-sdk[exa,parallel] @ git+https://github.com/dhruv-anand-aintech/anysearch.git@main#subdirectory=python"
pip install "anysearch-sdk[all] @ git+https://github.com/dhruv-anand-aintech/anysearch.git@main#subdirectory=python"
uv add "anysearch-sdk[exa,tavily,brave] @ git+https://github.com/dhruv-anand-aintech/anysearch.git@main#subdirectory=python"
```

REST-only providers (`brave`, `serper`, `you`, `jina`, `kagi`, `searchapi`,
`google-pse`, `searxng`) need no extra dependency — the extra name still resolves so
the selection syntax is uniform.

## Providers

| Provider | Name / aliases | Env var(s) | Extra (native SDK) |
| --- | --- | --- | --- |
| Exa | `exa` | `EXA_API_KEY` | `exa-py` |
| Parallel | `parallel` | `PARALLEL_API_KEY` | `parallel-web` |
| Tavily | `tavily` | `TAVILY_API_KEY` | `tavily-python` |
| Brave | `brave` | `BRAVE_API_KEY` | — |
| Keiro | `keiro` | `KEIRO_API_KEY` | — |
| Linkup | `linkup` | `LINKUP_API_KEY` | `linkup-sdk` |
| Perplexity | `perplexity`, `pplx` | `PERPLEXITY_API_KEY` | `perplexityai` |
| Serper | `serper` | `SERPER_API_KEY` | — |
| SerpApi | `serpapi`, `serp` | `SERPAPI_API_KEY` | `google-search-results` (engine: bing, baidu, yandex, …) |
| SearchApi | `searchapi` | `SEARCHAPI_API_KEY` | — |
| You.com | `you`, `ydc` | `YDC_API_KEY` | — |
| Jina | `jina` | `JINA_API_KEY` | — |
| Kagi | `kagi` | `KAGI_API_KEY` | — |
| Firecrawl | `firecrawl` | `FIRECRAWL_API_KEY` | `firecrawl-py` |
| Google PSE | `google_pse`, `google` | `GOOGLE_PSE_API_KEY` + `GOOGLE_PSE_CX` | — |
| SearXNG | `searxng`, `searx` | `SEARXNG_BASE_URL` (no key) | — |
| DuckDuckGo | `duckduckgo`, `ddg` | none (keyless fallback) | `ddgs` |

## Unified parameters

| Param | Type | Notes |
| --- | --- | --- |
| `query` | `str` | required |
| `max_results` | `int` | honored everywhere (sliced client-side when needed) |
| `search_type` | `"web" \| "news"` | |
| `country` | `str` | ISO 3166-1 alpha-2 |
| `language` | `str` | ISO 639-1 |
| `include_domains` / `exclude_domains` | `list[str]` | |
| `start_published_date` / `end_published_date` | `str` | ISO 8601 / `YYYY-MM-DD` |
| `safe_search` | `"off" \| "moderate" \| "strict"` | |
| `mode` | `"fast" \| "balanced" \| "deep"` | depth/quality knob, mapped per provider |
| `answer` | `bool` | synthesized, cited answer where supported |
| `include_content` | `bool` | full page text where supported |
| `include_summary` | `bool` | per-result AI summary where supported |
| `highlights` | `bool` | query-relevant excerpts where supported |
| `extra` | `dict` | raw provider-specific passthrough |

Unsupported parameters are handled by `on_unsupported` (`"warn"` default, or `"ignore"`
/ `"error"`). Unknown keyword arguments are forwarded to the provider as `extra`.

### Common response shape

`search()` returns a `SearchResponse`:

```python
resp.provider          # "exa"
resp.query             # "..."
resp.answer            # synthesized answer, if any
resp.results           # list[SearchResult]
resp.urls              # [r.url for r in results]
resp.to_dict()         # JSON-serializable

r = resp.results[0]
r.title, r.url, r.snippet, r.text, r.summary, r.highlights, r.score, r.published_date, r.author, r.source
r.raw                  # the provider's raw result
```

## Fallbacks, async, and the native escape hatch

```python
from anysearch import AnySearch

client = AnySearch(provider="exa", fallbacks=["tavily", "brave"])
resp = client.search("...", mode="deep")

# Async
resp = await client.asearch("...")

# Drop down to a provider's official SDK (requires the extra installed)
exa = anysearch.native("exa")        # -> exa_py.Exa instance
```

## MCP server

```bash
anysearch-mcp            # stdio MCP server
anysearch-mcp --probe    # also verify each provider with a tiny live query at startup
```

Tools exposed: `search`, `list_providers`, `check_providers`, and `migrate_codebase`
(scans a repo for direct search-API usage and suggests unified replacements). See the
repo root README for client configuration examples.

## FastAPI proxy

The proxy is a small search gateway inspired by LiteLLM Proxy: bearer-key auth,
provider routing/fallbacks, OpenAI-style `/v1/models` and `/v1/search`, native
`/search`, health checks, and simple in-process request limits.

```bash
pip install "anysearch-sdk[proxy] @ git+https://github.com/dhruv-anand-aintech/anysearch.git@main#subdirectory=python"

export ANYSEARCH_PROXY_KEYS="dev-key"
export EXA_API_KEY="..."
anysearch-proxy
```

```bash
curl -H "Authorization: Bearer dev-key" http://localhost:4000/v1/models
curl -X POST http://localhost:4000/v1/search \
  -H "Authorization: Bearer dev-key" \
  -H "Content-Type: application/json" \
  -d '{"model":"exa","query":"best vector databases","max_results":3}'
```

Useful env vars: `ANYSEARCH_PROXY_KEYS`, `ANYSEARCH_PROXY_ADMIN_KEYS`,
`ANYSEARCH_PROXY_REQUIRE_AUTH=0`, `ANYSEARCH_PROXY_REQUEST_LIMIT`,
`ANYSEARCH_PROXY_HOST`, and `ANYSEARCH_PROXY_PORT`.
