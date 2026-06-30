# Provider capability matrix

**Interactive matrix:** [compare-anysearch.ainorthstar.tech](https://compare-anysearch.ainorthstar.tech)
(drag columns, sort by capability, tooltips with docs links). This file is the static
reference; regenerate the site data with `npm run matrix:sync` from the repo root.

`anysearch` exposes one interface, but providers differ in what they support. The table
below shows which **unified parameters** each provider honors. Parameters a provider
can't honor are dropped (with a warning) by default, or you can pass
`on_unsupported="error"` / `onUnsupported: "error"` to fail loudly, or `"ignore"` to
drop silently.

Legend: ✅ supported · — not supported (the param is ignored for that provider).

| Provider | domains | country | language | date | safe_search | mode | engine | answer | content | summary | highlights | news |
| --- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| **exa** | ✅ | ✅ | — | ✅ | ✅ | ✅ | — | — | ✅ | ✅ | ✅ | ✅ |
| **parallel** | ✅ | ✅ | — | ✅ | — | ✅ | — | — | ✅ | — | ✅ | — |
| **tavily** | ✅ | ✅ | — | ✅ | — | ✅ | — | ✅ | ✅ | — | — | ✅ |
| **brave** | — | ✅ | ✅ | ✅ | ✅ | — | — | — | — | — | ✅ | ✅ |
| **keiro** | — | — | — | — | — | ✅ | — | — | ✅ | — | — | — |
| **linkup** | ✅ | — | — | ✅ | — | ✅ | — | ✅ | ✅ | — | — | — |
| **perplexity** | ✅ | — | ✅ | — | — | — | — | — | ✅ | — | — | — |
| **gemini** | — | — | — | — | — | — | — | ✅ | — | — | — | — |
| **serper** | — | ✅ | ✅ | — | — | — | — | ✅* | — | — | — | ✅ |
| **serpapi** (`engine=…`) | — | ✅† | ✅† | — | ✅† | — | ✅ | ✅* | — | — | — | ✅† |
| **searchapi** | — | ✅ | ✅ | — | — | — | — | ✅* | — | — | — | ✅ |
| **you** | ✅ | ✅ | — | — | — | — | — | — | — | — | ✅ | — |
| **jina** | — | — | — | — | — | — | — | — | ✅ | — | — | — |
| **kagi** | — | — | — | — | — | — | — | — | — | — | — | — |
| **firecrawl** | — | ✅ | — | — | — | — | — | — | ✅ | — | — | ✅ |
| **google_pse** | ✅‡ | ✅ | ✅ | ✅ | ✅ | — | — | — | — | — | — | — |
| **searxng** | — | — | ✅ | — | ✅ | — | — | ✅§ | — | — | — | — |
| **duckduckgo** | — | ✅ | — | — | ✅ | — | — | — | — | — | — | — |

\* Serper / SerpApi / SearchApi surface an answer only when the SERP includes an answer
box; it is not requested explicitly.
‡ Google PSE supports a single include **or** exclude domain (first one wins) via
`siteSearch`.
§ SearXNG returns instant-answer text from its `answers` field when available.
† SerpApi: locale/safe/news params vary by `engine` (see matrix columns per backend).

## SerpApi engines

The [capability matrix](https://compare-anysearch.ainorthstar.tech) lists each SerpApi backend as its
own column (**Google · SerpApi**, **Bing · SerpApi**, **Baidu · SerpApi**, etc.) so capabilities
are compared per engine, not as a single aggregated SerpApi row.

Pass `engine` on `search()` (or set `AnySearch(provider="serpapi", provider_config={"serpapi": {"engine": "bing"}})`):

```python
client.search("query", provider="serpapi", engine="bing")
client.search("query", provider="serpapi", engine="baidu", country="cn")
client.search("headlines", provider="serpapi", engine="bing", search_type="news")
```

Common web engines: `google`, `bing`, `baidu`, `yandex`, `duckduckgo`, `yahoo`. See
[SerpApi Search API](https://serpapi.com/search-api) for the full catalog and engine-specific
parameters (pass via `extra`).

## Notes on `mode`

The matrix **Mode** row lists which unified tiers each API actually exposes:

- **fast** — a documented low-latency / lightweight search preset (not “less content” shortcuts).
- **balanced** — the default search tier.
- **deep** — an AI synthesis / multi-step research mode (not richer snippets, scraping, or `include_content`).

The [comparison matrix](https://compare-anysearch.ainorthstar.tech) documents search and
synthesis/research APIs in one column when they share an API key (**Tavily**, **Perplexity**,
**You**, **Brave**, **Parallel**).

| Column | Matrix modes | Native API |
| --- | --- | --- |
| exa | fast, balanced, deep | `/search` `type`: instant/fast, auto, deep/deep-lite/deep-reasoning |
| tavily | fast, balanced, deep | Search `search_depth`; Research API `model`: mini/auto, pro |
| parallel | fast, balanced, deep | Search `mode`: basic/advanced; Task API `processor`: Lite/Base, Core, Pro/Ultra |
| linkup | fast, balanced, deep | `depth` + `outputType=sourcedAnswer` for cited synthesis |
| perplexity | balanced, deep | Search API `POST /search` (SDK); Sonar `POST /chat/completions` — `sonar`, `sonar-pro` |
| **gemini** | balanced | `generateContent` + `google_search` tool (grounded synthesis) |
| brave | balanced, deep | Web/news SERP; Answers `/chat/completions` (`enable_research` → deep) |
| keiro | fast, balanced, deep | v2 search endpoints; REST adapter posts `apiKey` in the JSON body |
| you | fast, balanced, deep | `POST /v1/search` (SDK); Research `research_effort`: lite, standard, deep, exhaustive |
| serper, serpapi, searchapi, google_pse, searxng, duckduckgo, jina, firecrawl, kagi | balanced | No fast or synthesis depth preset |

anysearch SDK today implements **search** endpoints for these providers; merged matrix rows also
document synthesis APIs (Sonar, Tavily Research, etc.) you can call directly. Tavily `mode=deep` in
the SDK still maps to Search `advanced` retrieval — matrix `deep` is the Research API `pro` tier only.

## Content fields, by intent

- **`snippet`** — the short description the engine returns. Available almost everywhere.
- **`text`** — full page content. Request with `include_content` (exa, tavily,
  parallel, keiro, linkup, perplexity, jina, firecrawl, you).
- **`summary`** — an AI-generated per-result summary. Request with `include_summary`
  (exa).
- **`highlights`** — query-relevant excerpts. Request with `highlights` (exa, brave,
  parallel, you).
- **`answer`** (top-level on the response) — a synthesized, often cited answer to the
  whole query. Request with `answer` (gemini, tavily, linkup; opportunistic on serper/serpapi/
  searchapi/searxng).

## Configuration reference

| Provider | Credentials | Optional |
| --- | --- | --- |
| exa | `EXA_API_KEY` | extra `exa` → `exa-py` |
| parallel | `PARALLEL_API_KEY` | extra `parallel` → `parallel-web` |
| tavily | `TAVILY_API_KEY` | extra `tavily` → `tavily-python` |
| brave | `BRAVE_API_KEY` | — |
| keiro | `KEIRO_API_KEY` | — |
| linkup | `LINKUP_API_KEY` | extra `linkup` → `linkup-sdk` |
| perplexity | `PERPLEXITY_API_KEY` | extra `perplexity` → `perplexityai` |
| gemini | `GEMINI_API_KEY` | extra `gemini` → `google-genai`; optional `provider_config.gemini.model` |
| serper | `SERPER_API_KEY` | — |
| serpapi | `SERPAPI_API_KEY` | extra `serpapi` → `google-search-results` |
| searchapi | `SEARCHAPI_API_KEY` | — |
| you | `YDC_API_KEY` | — |
| jina | `JINA_API_KEY` | — |
| kagi | `KAGI_API_KEY` | — |
| firecrawl | `FIRECRAWL_API_KEY` | extra `firecrawl` → `firecrawl-py` |
| google_pse | `GOOGLE_PSE_API_KEY` + `GOOGLE_PSE_CX` | — |
| searxng | `SEARXNG_BASE_URL` (no key; optional `SEARXNG_API_KEY`) | — |
| duckduckgo | none (keyless fallback) | extra `duckduckgo` → `ddgs` |

Override the API key or base URL per call/client with `api_key` / `base_url`
(`apiKey` / `baseUrl` in JS), or set `ANYSEARCH_PROVIDER` to pin a default provider.
