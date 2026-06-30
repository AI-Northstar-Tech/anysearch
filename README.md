# anysearch

**One interface for every web search API.** `anysearch` is an adapter layer for search
providers — inspired by [LiteLLM](https://github.com/BerriAI/litellm) (one interface for
every LLM) and [vector-io](https://github.com/AI-Northstar-Tech/vector-io) (one interface
for every vector DB). Call Exa, Parallel, Brave, Tavily, Keiro, SerpAPI, Perplexity, Linkup,
Firecrawl, and 8 more through a **single function**, with **common parameters** and a
**common response shape**, in **Python and JavaScript/TypeScript** — plus a **stdio MCP
server** and optional **FastAPI proxy** that adapt to whatever API keys you have set.

```python
# Python
import anysearch
resp = anysearch.search("who won the 2026 super bowl?", max_results=5)
```

```ts
// JavaScript / TypeScript
import { search } from "anysearch";
const resp = await search("who won the 2026 super bowl?", { maxResults: 5 });
```

If no `provider` is given, anysearch auto-selects one from the API keys present in your
environment (falling back to keyless DuckDuckGo), so the same code runs anywhere.

## Why

Every search API has a different request format, a different auth scheme, and a
different response shape. Swapping providers — or supporting several — means rewriting
glue code each time. `anysearch` normalizes all of it:

- **Lowest-common-denominator params** that work everywhere (`query`, `max_results`,
  `country`, `language`, domain filters, date filters, `safe_search`, web/news).
- **Unified "extra param modes"** for richer features mapped per provider: `mode`
  (fast/balanced/deep), `answer` (synthesized answers), `include_content` (full page
  text), `include_summary` (AI summaries), `highlights` (relevant excerpts).
- **Raw passthrough** via `extra` / `provider_params` for anything provider-specific.
- **One response shape**: `title, url, snippet, text, summary, highlights, score,
  published_date, author, source, raw` + a top-level `answer`.

## Providers (17)

| Provider | Name / aliases | Env var(s) | Highlights of support |
| --- | --- | --- | --- |
| [Exa](https://exa.ai) | `exa` | `EXA_API_KEY` | content, summary, highlights, domains, dates, news |
| [Parallel](https://parallel.ai) | `parallel` | `PARALLEL_API_KEY` | content, highlights, domains, mode |
| [Tavily](https://tavily.com) | `tavily` | `TAVILY_API_KEY` | answer, content, domains, mode, news |
| [Brave](https://brave.com/search/api/) | `brave` | `BRAVE_API_KEY` | highlights, country, language, dates, news |
| [Keiro](https://keirolabs.cloud) | `keiro` | `KEIRO_API_KEY` | source-cited snippets, content endpoint, mode |
| [Linkup](https://linkup.so) | `linkup` | `LINKUP_API_KEY` | answer, content, domains, dates, mode |
| [Perplexity](https://docs.perplexity.ai) | `perplexity`, `pplx` | `PERPLEXITY_API_KEY` | content, domains, language |
| [Gemini](https://ai.google.dev/gemini-api/docs/google-search) | `gemini`, `google_gemini` | `GEMINI_API_KEY` | Google Search grounding, answer, source chunks |
| [Serper](https://serper.dev) | `serper` | `SERPER_API_KEY` | answer, country, language, news |
| [SerpApi](https://serpapi.com) | `serpapi`, `serp` | `SERPAPI_API_KEY` | engine (bing/baidu/yandex/…), country, language, safe, news, answer* |
| [SearchApi](https://searchapi.io) | `searchapi` | `SEARCHAPI_API_KEY` | answer, country, language, news |
| [You.com](https://you.com) | `you`, `ydc` | `YDC_API_KEY` | highlights, content, domains |
| [Jina](https://jina.ai/reader) | `jina` | `JINA_API_KEY` | content |
| [Kagi](https://help.kagi.com/kagi/api/search.html) | `kagi` | `KAGI_API_KEY` | snippets |
| [Firecrawl](https://firecrawl.dev) | `firecrawl` | `FIRECRAWL_API_KEY` | content, country, news |
| [Google PSE](https://developers.google.com/custom-search) | `google_pse`, `google` | `GOOGLE_PSE_API_KEY` + `GOOGLE_PSE_CX` | country, language, safe, domains |
| [SearXNG](https://docs.searxng.org) | `searxng`, `searx` | `SEARXNG_BASE_URL` (no key) | answer, language, safe |
| [DuckDuckGo](https://duckduckgo.com) | `duckduckgo`, `ddg` | none (keyless) | snippets |

See [`docs/PROVIDERS.md`](docs/PROVIDERS.md) for the full capability matrix.

## Install

Install from the latest **`main`** on GitHub (not published to PyPI/npm yet).

### Python (pip / uv)

```bash
pip install "git+https://github.com/dhruv-anand-aintech/anysearch.git@main#subdirectory=python"

# Optional: provider native SDKs via extras (for anysearch.native("exa"), etc.)
pip install "anysearch-sdk[exa,parallel] @ git+https://github.com/dhruv-anand-aintech/anysearch.git@main#subdirectory=python"
pip install "anysearch-sdk[all] @ git+https://github.com/dhruv-anand-aintech/anysearch.git@main#subdirectory=python"

uv add "anysearch-sdk @ git+https://github.com/dhruv-anand-aintech/anysearch.git@main#subdirectory=python"
uv add "anysearch-sdk[exa,tavily,brave] @ git+https://github.com/dhruv-anand-aintech/anysearch.git@main#subdirectory=python"
uv add "anysearch-sdk[proxy] @ git+https://github.com/dhruv-anand-aintech/anysearch.git@main#subdirectory=python"
```

The base install works for **every** provider (REST via `httpx`). Per-provider extras
add that provider's official SDK for the `anysearch.native("<provider>")` escape hatch.

### JavaScript / TypeScript (npm)

```bash
npm install github:dhruv-anand-aintech/anysearch#main:js
```

No runtime dependencies (uses built-in `fetch`). Provider SDKs are optional and only
needed for `native()`.

## Usage

### Common parameters

| Param (py / ts) | Notes |
| --- | --- |
| `query` | required |
| `max_results` / `maxResults` | honored everywhere |
| `search_type` / `searchType` | `"web"` or `"news"` |
| `country`, `language` | ISO 3166-1 alpha-2 / ISO 639-1 |
| `include_domains` / `includeDomains`, `exclude_domains` / `excludeDomains` | |
| `start_published_date`…, `end_published_date`… | ISO 8601 / `YYYY-MM-DD` |
| `safe_search` / `safeSearch` | `off` / `moderate` / `strict` |
| `mode` | `fast` / `balanced` / `deep` (depth/quality knob, mapped per provider) |
| `answer` | synthesized, cited answer where supported |
| `include_content` / `includeContent` | full page text where supported |
| `include_summary` / `includeSummary` | per-result AI summary where supported |
| `highlights` | query-relevant excerpts where supported |
| `extra` | raw provider-specific passthrough |

Parameters a provider can't honor are governed by `on_unsupported` / `onUnsupported`:
`"warn"` (default), `"ignore"`, or `"error"`.

### Provider selection & fallbacks

```python
from anysearch import AnySearch
client = AnySearch(provider="exa", fallbacks=["tavily", "brave"])
resp = client.search("rust async runtimes", mode="deep")
print(resp.answer, len(resp.results))
```

```ts
import { AnySearch } from "anysearch";
const client = new AnySearch({ provider: "exa", fallbacks: ["tavily", "brave"] });
const resp = await client.search("rust async runtimes", { mode: "deep" });
```

Set `ANYSEARCH_PROVIDER` to force a default provider for the whole process.

## FastAPI proxy

The Python package includes an optional proxy server inspired by LiteLLM Proxy: bearer
auth, centralized provider routing/fallbacks, OpenAI-style `/v1/models` and `/v1/search`,
native `/search`, health checks, and simple in-process request limits.

```bash
export ANYSEARCH_PROXY_KEYS="dev-key"
export EXA_API_KEY="..."
anysearch-proxy

curl -X POST http://localhost:4000/v1/search \
  -H "Authorization: Bearer dev-key" \
  -H "Content-Type: application/json" \
  -d '{"model":"exa","query":"best vector databases","max_results":3}'
```

## MCP server

A self-contained stdio MCP server ships with both SDKs. It exposes the available
providers dynamically based on which API keys are set (and, with `--probe`, which keys
actually work).

```bash
# Python
anysearch-mcp
anysearch-mcp --probe

# Node
npx anysearch-mcp
```

Example client config (Cursor / Claude Desktop style):

```json
{
  "mcpServers": {
    "anysearch": {
      "command": "anysearch-mcp",
      "env": { "EXA_API_KEY": "...", "TAVILY_API_KEY": "...", "BRAVE_API_KEY": "..." }
    }
  }
}
```

### Tools

- **`search`** — unified search. The `provider` enum adapts to your configured keys.
- **`list_providers`** — every provider, its capabilities, and whether it's configured.
- **`check_providers`** — runs a tiny live query to report which providers actually work.
- **`migrate_codebase`** — scans a repo for direct search-API usage (SDK imports, client
  constructors, REST endpoints for all 17 providers) and returns precise call sites with
  suggested unified `anysearch` replacements, so an agent can mechanically migrate it.

## Provider capability matrix

Interactive comparison of all 17 providers (unified params + response fields), same
interaction model as [compare.ainorthstar.tech](https://compare.ainorthstar.tech/):

**https://compare-anysearch.ainorthstar.tech**

Source: `docs/tools/search_matrix/` · Worker: `worker/matrix.js` · Regenerate with
`npm run matrix:sync` after provider changes.

## Repository layout

```
anysearch/
├── python/   # anysearch-sdk — SDK + anysearch-mcp (install from GitHub, see above)
├── js/       # anysearch — SDK + anysearch-mcp (install from GitHub, see above)
├── worker/   # Cloudflare Worker for the compare matrix site
├── docs/     # PROVIDERS.md + search_matrix data
└── scripts/  # generate_search_matrix_data.py
```

## Development

```bash
# Python
cd python && python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]" && pytest && ruff check src

# JavaScript
cd js && npm install && npm run build && npm test
```

## License

MIT — see [LICENSE](LICENSE).
