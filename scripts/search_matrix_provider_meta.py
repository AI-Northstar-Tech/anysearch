"""Official docs-backed metadata for the search capability matrix.

All `source_url` values must point at provider documentation (never the anysearch repo).
"""

from __future__ import annotations

# Primary docs + website per slug (overrides generator defaults where set).
LINKS: dict[str, dict[str, str]] = {
    "exa": {"docs": "https://exa.ai/docs/reference/search", "website": "https://exa.ai"},
    "parallel": {
        "docs": "https://docs.parallel.ai/search/modes",
        "website": "https://parallel.ai",
    },
    "tavily": {
        "docs": "https://docs.tavily.com/documentation/api-reference/endpoint/search",
        "website": "https://tavily.com",
    },
    "brave": {
        "docs": "https://api-dashboard.search.brave.com/app/documentation/web-search/get-started",
        "website": "https://brave.com/search/api/",
    },
    "keiro": {
        "docs": "https://keirolabs.cloud/",
        "website": "https://keirolabs.cloud",
    },
    "linkup": {
        "docs": "https://docs.linkup.so/pages/documentation/endpoints/search/overview",
        "website": "https://www.linkup.so",
    },
    "perplexity": {
        "docs": "https://docs.perplexity.ai/api-reference/search-post",
        "website": "https://www.perplexity.ai",
    },
    "gemini": {
        "docs": "https://ai.google.dev/gemini-api/docs/google-search",
        "website": "https://ai.google.dev/gemini-api",
    },
    "serper": {"docs": "https://serper.dev/docs", "website": "https://serper.dev"},
    "serpapi": {"docs": "https://serpapi.com/search-api", "website": "https://serpapi.com"},
    "searchapi": {
        "docs": "https://www.searchapi.io/docs/google",
        "website": "https://www.searchapi.io",
    },
    "you": {
        "docs": "https://you.com/docs/search/overview",
        "website": "https://you.com",
    },
    "jina": {"docs": "https://jina.ai/reader/", "website": "https://jina.ai"},
    "kagi": {
        "docs": "https://help.kagi.com/kagi/api/search.html",
        "website": "https://kagi.com",
    },
    "firecrawl": {
        "docs": "https://docs.firecrawl.dev/api-reference/endpoint/search",
        "website": "https://www.firecrawl.dev",
    },
    "google_pse": {
        "docs": "https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list",
        "website": "https://programmablesearchengine.google.com",
    },
    "searxng": {
        "docs": "https://docs.searxng.org/dev/search_api.html",
        "website": "https://docs.searxng.org",
    },
    "duckduckgo": {
        "docs": "https://pypi.org/project/ddgs/",
        "website": "https://duckduckgo.com",
    },
}

# PyPI or provider install docs for optional native SDK extras (never anysearch repo).
EXTRA_SOURCES: dict[str, str] = {
    "exa": "https://pypi.org/project/exa-py/",
    "parallel": "https://pypi.org/project/parallel-web/",
    "tavily": "https://pypi.org/project/tavily-python/",
    "keiro": "https://pypi.org/project/keirolabs/",
    "linkup": "https://docs.linkup.so/pages/sdk/python/python",
    "perplexity": "https://pypi.org/project/perplexityai/",
    "gemini": "https://pypi.org/project/google-genai/",
    "serpapi": "https://pypi.org/project/google-search-results/",
    "firecrawl": "https://pypi.org/project/firecrawl-py/",
    "duckduckgo": "https://pypi.org/project/ddgs/",
}

# Env var documentation (authentication / configuration).
ENV_SOURCES: dict[str, str] = {
    "exa": "https://exa.ai/docs/reference/quickstart",
    "parallel": "https://docs.parallel.ai/getting-started/overview",
    "tavily": "https://docs.tavily.com/documentation/api-reference/endpoint/search",
    "brave": "https://api-dashboard.search.brave.com/app/documentation/web-search/get-started",
    "keiro": "https://keirolabs.cloud/",
    "linkup": "https://docs.linkup.so/pages/documentation/endpoints/search/reference",
    "perplexity": "https://docs.perplexity.ai/docs/search/quickstart",
    "gemini": "https://ai.google.dev/gemini-api/docs/api-key",
    "serper": "https://serper.dev/docs",
    "serpapi": "https://serpapi.com/search-api",
    "searchapi": "https://www.searchapi.io/docs/google",
    "you": "https://you.com/docs/api-reference/search/v1-search",
    "jina": "https://jina.ai/reader/",
    "kagi": "https://help.kagi.com/kagi/api/search.html",
    "firecrawl": "https://docs.firecrawl.dev/api-reference/endpoint/search",
    "google_pse": "https://developers.google.com/custom-search/v1/using_rest",
    "searxng": "https://docs.searxng.org/admin/settings/settings_search/",
    "duckduckgo": "https://pypi.org/project/ddgs/",
}

MODE_META: dict[str, dict] = {
    "exa": {
        "values": ["fast", "balanced", "deep"],
        "source": "https://exa.ai/docs/reference/search-api-guide",
        "comment": (
            "POST /search `type`: `instant`/`fast` (latency), `auto` (balanced), `deep` / "
            "`deep-lite` / `deep-reasoning` (agentic multi-source synthesis; optional `output_schema`). "
            "anysearch: fast→fast, balanced→auto, deep→deep."
        ),
    },
    "tavily": {
        "values": ["fast", "balanced", "deep"],
        "source": "https://docs.tavily.com/documentation/best-practices/best-practices-search",
        "comment": (
            "**Search API** `search_depth`: `ultra-fast`/`fast`→fast, `basic`→balanced (`include_answer` "
            "is a short blurb, not deep research). **Research API** (`POST /research`) `model`: "
            "`mini`/`auto`→balanced, `pro`→deep (multi-agent cited report). Same `TAVILY_API_KEY`."
        ),
    },
    "parallel": {
        "values": ["fast", "balanced", "deep"],
        "source": "https://docs.parallel.ai/search/modes",
        "comment": (
            "**Search API** `mode`: `basic`→fast, `advanced`→balanced (richer retrieval, not synthesis). "
            "**Task API** (`POST /v1/tasks/runs`) `processor`: Lite/Base→fast, Core→balanced, "
            "Pro/Ultra→deep (structured output with citations). Same `PARALLEL_API_KEY`."
        ),
    },
    "linkup": {
        "values": ["fast", "balanced", "deep"],
        "source": "https://docs.linkup.so/pages/documentation/endpoints/search/overview",
        "comment": (
            "Native `depth`: `fast`, `standard` (balanced), or `deep` (multi-iteration agentic "
            "search-and-scrape). Cited synthesis uses `outputType=sourcedAnswer` (`answer=true` in "
            "anysearch), including at `deep` depth. anysearch: fast/balanced/deep→matching depth."
        ),
    },
    "keiro": {
        "values": ["fast", "balanced", "deep"],
        "source": "https://keirolabs.cloud/",
        "comment": (
            "v2 Search `mode`: `light`→fast, `ai`→balanced, `deep`→deep. anysearch uses "
            "`/api/v2/search/flash` for fast mode, `/api/v2/keiro` by default, "
            "and `/api/v2/search/content` for full-text content."
        ),
    },
    "brave": {
        "values": ["balanced", "deep"],
        "source": "https://api-dashboard.search.brave.com/app/documentation/web-search",
        "comment": (
            "**Web/news SERP** (`/res/v1/web/search`) → matrix `balanced`. **Answers API** "
            "(`POST /res/v1/chat/completions`, `model=brave`) → balanced (single-pass grounded answer); "
            "`enable_research=true` (streaming)→deep. Same `BRAVE_API_KEY`."
        ),
    },
    "keiro": {
        "values": ["fast", "balanced", "deep"],
        "source": "https://keirolabs.cloud/",
        "comment": (
            "v2 search endpoints exposed through `mode`: balanced uses `/api/v2/keirolabs`, "
            "fast/deep use `/api/v2/search/fast`, and content requests use `/api/v2/search/content`. "
            "KeiroLabs expects the API key in the JSON body."
        ),
    },
    "jina": {
        "values": ["balanced"],
        "source": "https://jina.ai/reader/",
        "comment": (
            "Reader Search has no vendor fast/synthesis mode knob. Default returns SERP + optional "
            "page markdown; `X-Respond-With: no-content` is a fetch shortcut, not a latency tier."
        ),
    },
    "perplexity": {
        "values": ["balanced", "deep"],
        "source": "https://docs.perplexity.ai/docs/search/quickstart",
        "comment": (
            "**Search API** (`POST /search`) → matrix `balanced`: raw ranked `results[]` (anysearch SDK). "
            "**Sonar** (`POST /chat/completions`) → model `sonar`→balanced (grounded answer + citations), "
            "`sonar-pro`→deep (multi-source research synthesis). Same `PERPLEXITY_API_KEY`."
        ),
    },
    "gemini": {
        "values": ["balanced"],
        "source": "https://ai.google.dev/gemini-api/docs/google-search",
        "comment": (
            "`generateContent` with `tools: [{google_search: {}}]` — model decides when to search "
            "and returns synthesized text plus `groundingMetadata` sources (use `answer=true` in anysearch). "
            "Default model `gemini-2.5-flash` via `provider_config.gemini.model`."
        ),
    },
    "firecrawl": {
        "values": ["balanced"],
        "source": "https://docs.firecrawl.dev/features/search",
        "comment": (
            "Single search tier (title, URL, description). `scrapeOptions` fetches page bodies "
            "but is not an AI synthesis `mode`."
        ),
    },
    "you": {
        "values": ["fast", "balanced", "deep"],
        "source": "https://you.com/docs/search/overview",
        "comment": (
            "**Search API** (`POST /v1/search`) → matrix `balanced` (ranked snippets, SDK). "
            "**Research API** (`POST /v1/research`) → `research_effort`: `lite`→fast, `standard`→balanced, "
            "`deep` / `exhaustive`→deep (cited synthesis). Same `YDC_API_KEY`."
        ),
    },
    "kagi": {
        "values": ["balanced"],
        "source": "https://help.kagi.com/kagi/api/search.html",
        "comment": (
            "No request `mode`; snippet length comes from account Settings → Search."
        ),
    },
    "serper": {
        "values": ["balanced"],
        "source": "https://serper.dev/docs",
        "comment": (
            "Google SERP proxy: one ranked result style per call (no fast/deep API knob). "
            "Matrix `balanced` = standard /search or /news endpoint."
        ),
    },
    "serpapi": {
        "values": ["balanced"],
        "source": "https://serpapi.com/search-api",
        "comment": (
            "Aggregated Google engine API: no latency/depth parameter on the search call. "
            "Matrix `balanced` = default engine JSON response."
        ),
    },
    "searchapi": {
        "values": ["balanced"],
        "source": "https://www.searchapi.io/docs/google",
        "comment": (
            "Google engine wrapper: single SERP depth per request (no native fast/deep tier)."
        ),
    },
    "google_pse": {
        "values": ["balanced"],
        "source": "https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list",
        "comment": (
            "Custom Search JSON API: no search-depth or speed preset—only `num`, `sort`, "
            "and `siteSearch` filters. Matrix `balanced` = default `cse.list` behavior."
        ),
    },
    "searxng": {
        "values": ["balanced"],
        "source": "https://docs.searxng.org/dev/search_api.html",
        "comment": (
            "Meta-search JSON API: result richness depends on configured engines, not a "
            "global depth flag. Matrix `balanced` = default instance search."
        ),
    },
    "duckduckgo": {
        "values": ["balanced"],
        "source": "https://pypi.org/project/ddgs/",
        "comment": (
            "Keyless DDGS client: instant web results without a depth parameter. "
            "Matrix `balanced` = default `text()` search."
        ),
    },
}

PRICING_META: dict[str, dict[str, str]] = {
    "exa": {
        "value": "fast/balanced: $7; deep: $12; deep reasoning: $15",
        "source_url": "https://exa.ai/pricing",
        "comment": "Per 1K requests with up to 10 results; summaries and additional results are billed separately.",
    },
    "parallel": {
        "value": "fast/search: $5; balanced/task: $10-$25; deep/task: $100-$300+",
        "source_url": "https://docs.parallel.ai/resources/pricing",
        "comment": "Search API is $5/1K requests; Task processors map roughly from Base/Core to Pro/Ultra for deeper modes.",
    },
    "tavily": {
        "value": "fast/basic: ~$8; balanced/advanced: ~$16; deep/research: plan/model dependent",
        "source_url": "https://help.tavily.com/articles/8816424538-pricing",
        "comment": "Uses API credits; pay-as-you-go credits are listed at $0.008/credit, with higher-depth calls consuming more credits.",
    },
    "brave": {
        "value": "balanced/search: $5-$9; deep/answers: $4 + tokens",
        "source_url": "https://brave.com/search/api/",
        "comment": "Search API pricing depends on Base AI vs Pro AI plan; Answers adds token charges.",
    },
    "keiro": {
        "value": "fast/balanced: ~$0.50; content: ~$1.50; batch: ~$0.50",
        "source_url": "https://keirolabs.cloud/",
        "comment": "Keiro docs list credit costs per v2 endpoint and headline cost per 1,000 searches.",
    },
    "linkup": {
        "value": "fast: €5; balanced/standard: €5; deep: €50",
        "source_url": "https://linkup-api.readme.io/reference/credits",
        "comment": "Fast and standard cost one credit/call; deep costs ten credits/call. Fast docs list €0.005/call.",
    },
    "perplexity": {
        "value": "search: $5; fast/sonar low: $5; balanced: $8-$10; deep/high/pro: $12-$22 + tokens",
        "source_url": "https://docs.perplexity.ai/getting-started/pricing",
        "comment": "Search API is request-only; Sonar tiers add token charges and request fees by context size/search type.",
    },
    "gemini": {
        "value": "balanced grounding: $35 + model tokens",
        "source_url": "https://cloud.google.com/generative-ai-app-builder/pricing",
        "comment": "Grounding with Google Search is billed per 1K grounded requests plus Gemini model token charges.",
    },
    "serper": {
        "value": "balanced: $1.00 starter; $0.30-$0.75 volume",
        "source_url": "https://serper.dev/",
        "comment": "Top-up credit pricing; exact per-1K rate decreases with larger credit packs.",
    },
    "serpapi": {
        "value": "balanced: $25 starter; ~$7.25-$15 volume",
        "source_url": "https://serpapi.com/pricing",
        "comment": "Monthly plan price divided by included searches; applies to all SerpApi engine rows.",
    },
    "searchapi": {
        "value": "balanced: published plans vary; roughly $2-$4+",
        "source_url": "https://www.searchapi.io/pricing",
        "comment": "Pricing is plan/volume based; verify current SearchApi.io plan before budgeting.",
    },
    "you": {
        "value": "search: $5; research lite: $12; deeper research: tier dependent",
        "source_url": "https://you.com/pricing",
        "comment": "Search API is $5/1K calls; Research API starts at $12/1K and increases by effort tier.",
    },
    "jina": {
        "value": "token-based; no fixed per-query CPM",
        "source_url": "https://jina.ai/reader/",
        "comment": "Reader/Search usage is priced by tokens/usage tiers rather than a fixed per-1K query price.",
    },
    "kagi": {
        "value": "not publicly itemized per 1K for Search API",
        "source_url": "https://help.kagi.com/kagi/api/overview.html",
        "comment": "Kagi documents pay-per-use API portal billing but not a stable public Search API CPM in docs.",
    },
    "firecrawl": {
        "value": "balanced/search: 1 credit; with scrape: +1 credit/result",
        "source_url": "https://docs.firecrawl.dev/api-reference/endpoint/search",
        "comment": "Convert credits to dollars from your Firecrawl plan; search without scrape costs one credit.",
    },
    "google_pse": {
        "value": "balanced: $5",
        "source_url": "https://support.google.com/programmable-search/answer/9069107",
        "comment": "Custom Search JSON API and Programmable Search Element paid API are listed at $5/1K queries.",
    },
    "searxng": {
        "value": "$0 API fee if self-hosted; infra/proxy costs separate",
        "source_url": "https://docs.searxng.org/",
        "comment": "Open-source self-hosted metasearch; operating costs depend on deployment.",
    },
    "duckduckgo": {
        "value": "$0 API fee via keyless DDGS client; unofficial/fragile",
        "source_url": "https://pypi.org/project/ddgs/",
        "comment": "No paid official web search API is used by anysearch's keyless fallback.",
    },
}

# Per-feature support overrides (when code supports more/less than capabilities frozenset).
SUPPORT_OVERRIDE: dict[str, dict[str, str]] = {
    "google_pse": {
        "domains": "partial",
        "date": "partial",
    },
    "perplexity": {
        "answer": "full",
        "country": "partial",
    },
    "you": {
        "answer": "full",
        "date": "partial",
        "content": "partial",
    },
    "brave": {
        "answer": "full",
        "content": "partial",
    },
    "tavily": {
        "content": "partial",
    },
    "parallel": {
        "answer": "full",
    },
    "keiro": {
        "content": "full",
    },
    "serpapi_yandex": {
        "news": "none",
    },
}

# Extra matrix footnotes (appended to generated provider notes).
MATRIX_NOTES: dict[str, str] = {
    "perplexity": (
        "Search API (`POST /search`) is in the anysearch SDK; Sonar (`POST /chat/completions`) "
        "is documented in the matrix but not wired in the SDK yet."
    ),
    "you": (
        "Search API (`POST /v1/search`) is in the anysearch SDK; Research API (`POST /v1/research`) "
        "is documented in the matrix but not wired in the SDK yet."
    ),
    "brave": (
        "Web/news Search API is in the anysearch SDK; Answers API (`/res/v1/chat/completions`) "
        "is documented in the matrix but not wired in the SDK yet."
    ),
    "parallel": (
        "Search API is in the anysearch SDK; Task API (`POST /v1/tasks/runs`) is documented "
        "in the matrix but not wired in the SDK yet."
    ),
    "keiro": (
        "SDK maps default v2 search to `/api/v2/keiro`, `mode=fast` to "
        "`/api/v2/search/flash`, and `include_content=true` to `/api/v2/search/content`."
    ),
    "tavily": (
        "Search API is in the anysearch SDK; Research API (`POST /research`) is documented "
        "in the matrix (use `tavily-python` `research()` / `get_research()`)."
    ),
    "keiro": (
        "KeiroLabs v2 search is wired in the anysearch SDK as REST-only. "
        "The provider expects `apiKey`, `query`, and `maxResults` in the JSON request body."
    ),
}

# Per-feature comments and doc anchors (slug → feature key → {source, comment}).
# Omitted keys fall back to generic labels from the generator.
FEATURE_META: dict[str, dict[str, dict[str, str]]] = {
    "exa": {
        "domains": {
            "source": "https://exa.ai/docs/reference/search",
            "comment": "`includeDomains` / `excludeDomains` on POST /search.",
        },
        "country": {
            "source": "https://exa.ai/docs/reference/search",
            "comment": "`userLocation` (ISO country code) biases results.",
        },
        "date": {
            "source": "https://exa.ai/docs/reference/search",
            "comment": "`startPublishedDate` / `endPublishedDate` (ISO dates).",
        },
        "safe_search": {
            "source": "https://exa.ai/docs/reference/search",
            "comment": "`moderation: true` enables content filtering.",
        },
        "content": {
            "source": "https://exa.ai/docs/reference/search",
            "comment": "`contents.text` (or highlights) in the request body.",
        },
        "summary": {
            "source": "https://exa.ai/docs/reference/search",
            "comment": "`contents.summary` returns an AI summary per result.",
        },
        "highlights": {
            "source": "https://exa.ai/docs/reference/search-best-practices",
            "comment": "`contents.highlights` — query-relevant excerpts (~10× fewer tokens than full text).",
        },
        "news": {
            "source": "https://exa.ai/docs/reference/search",
            "comment": "`category: news` or `type` tuned for news-style retrieval.",
        },
    },
    "tavily": {
        "domains": {
            "source": "https://docs.tavily.com/documentation/api-reference/endpoint/search",
            "comment": (
                "Search API: `include_domains` / `exclude_domains` (max 300). Research API has no domain filter."
            ),
        },
        "country": {
            "source": "https://docs.tavily.com/documentation/api-reference/endpoint/search",
            "comment": (
                "Search API `country` (topic `general` only). Not on Research API."
            ),
        },
        "date": {
            "source": "https://docs.tavily.com/documentation/api-reference/endpoint/search",
            "comment": (
                "Search API `start_date` / `end_date` or `time_range`. Research API has no date filter."
            ),
        },
        "answer": {
            "source": "https://docs.tavily.com/documentation/api-reference/endpoint/research",
            "comment": (
                "Search: `include_answer` (`basic`/`advanced`) short LLM blurb from results. "
                "Research: completed task `content` is a full cited research report."
            ),
        },
        "content": {
            "source": "https://docs.tavily.com/documentation/api-reference/endpoint/search",
            "comment": (
                "Search: `include_raw_content` per result. Research: `sources[]` URLs + optional `output_schema`."
            ),
        },
        "snippet": {
            "source": "https://docs.tavily.com/documentation/api-reference/endpoint/search",
            "comment": (
                "Search API ranked result snippets. Research API returns a report only — no SERP list."
            ),
        },
        "news": {
            "source": "https://docs.tavily.com/documentation/api-reference/endpoint/search",
            "comment": "Search API `topic`: `news`. Research API has no news topic.",
        },
    },
    "parallel": {
        "domains": {
            "source": "https://docs.parallel.ai/search/advanced-search-settings",
            "comment": (
                "Search API: `advanced_settings.source_policy` domain allow/deny. "
                "Task API has no domain filter knob."
            ),
        },
        "country": {
            "source": "https://docs.parallel.ai/search/advanced-search-settings",
            "comment": (
                "Search API `advanced_settings.location` (ISO 3166-1 alpha-2). Not on Task API."
            ),
        },
        "date": {
            "source": "https://docs.parallel.ai/search/advanced-search-settings",
            "comment": (
                "Search API `source_policy.after_date` for freshness. Task API has no date filter."
            ),
        },
        "answer": {
            "source": "https://docs.parallel.ai/task-api/guides/access-research-basis",
            "comment": (
                "Task API synthesized output plus `basis` (citations, reasoning, confidence). "
                "Search API returns ranked excerpts only."
            ),
        },
        "content": {
            "source": "https://docs.parallel.ai/api-reference/search/search",
            "comment": (
                "Search API: pre-compressed excerpts (`excerpt_settings` optional). "
                "Task API: text/JSON/markdown via `task_spec.output_schema`."
            ),
        },
        "snippet": {
            "source": "https://docs.parallel.ai/search/modes",
            "comment": (
                "Search API ranked result excerpts. Task API is not a snippet SERP — structured task output."
            ),
        },
        "highlights": {
            "source": "https://docs.parallel.ai/search/best-practices",
            "comment": "Ranked excerpts per URL are the default Search API payload (not Task API).",
        },
    },
    "linkup": {
        "domains": {
            "source": "https://docs.linkup.so/pages/documentation/endpoints/search/reference",
            "comment": "`includeDomains` / `excludeDomains` arrays on POST /v1/search.",
        },
        "date": {
            "source": "https://docs.linkup.so/pages/documentation/endpoints/search/reference",
            "comment": "`fromDate` / `toDate` (YYYY-MM-DD) filter sources by publication date.",
        },
        "answer": {
            "source": "https://docs.linkup.so/pages/documentation/endpoints/search/overview",
            "comment": "`outputType`: `sourcedAnswer` returns a cited natural-language answer.",
        },
        "content": {
            "source": "https://docs.linkup.so/pages/documentation/endpoints/search/overview",
            "comment": "`outputType`: `searchResults` with page content in standard/deep depths.",
        },
    },
    "keiro": {
        "content": {
            "source": "https://keirolabs.cloud/",
            "comment": (
                "`/api/v2/search/content` returns full page markdown (`full_text`) and optional chunks."
            ),
        },
        "snippet": {
            "source": "https://keirolabs.cloud/",
            "comment": "`results[]` include title, URL, snippet, score, and optional published date.",
        },
    },
    "brave": {
        "country": {
            "source": "https://api-dashboard.search.brave.com/app/documentation/web-search/get-started",
            "comment": (
                "`country` on web/news SERP. Answers API does not expose the same filters."
            ),
        },
        "language": {
            "source": "https://api-dashboard.search.brave.com/app/documentation/web-search/get-started",
            "comment": (
                "`search_lang` and `ui_lang` on web search. Not on Answers chat completions."
            ),
        },
        "date": {
            "source": "https://api-dashboard.search.brave.com/app/documentation/web-search/get-started",
            "comment": (
                "Web/news `freshness` presets (`pd`, `pw`, `pm`, `py`) or custom range. Answers: none."
            ),
        },
        "safe_search": {
            "source": "https://api-dashboard.search.brave.com/app/documentation/web-search/get-started",
            "comment": "Web/news `safesearch`: `off`, `moderate`, `strict`.",
        },
        "answer": {
            "source": "https://api-dashboard.search.brave.com/app/documentation/ai-grounding",
            "comment": (
                "Answers API: OpenAI-compatible grounded completion with citations. "
                "Web search returns SERP JSON only (no LLM answer field)."
            ),
        },
        "content": {
            "source": "https://api-dashboard.search.brave.com/app/documentation/ai-grounding",
            "comment": (
                "Answers API embeds cited source URLs in the completion. Web search has snippets, not full pages."
            ),
        },
        "snippet": {
            "source": "https://api-dashboard.search.brave.com/app/documentation/web-search/get-started",
            "comment": (
                "Web/news SERP snippets. Answers API has no ranked snippet list — use web search or citations."
            ),
        },
        "highlights": {
            "source": "https://api-dashboard.search.brave.com/app/documentation/web-search",
            "comment": "`extra_snippets=true` — up to 5 alternate excerpts per web result (Pro).",
        },
        "news": {
            "source": "https://api-dashboard.search.brave.com/app/documentation/web-search/get-started",
            "comment": "Dedicated `/res/v1/news/search` endpoint (not Answers API).",
        },
    },
    "keiro": {
        "content": {
            "source": "https://keirolabs.cloud/",
            "comment": "`include_content=true` routes to `/api/v2/search/content` and maps `full_text`.",
        },
        "snippet": {
            "source": "https://keirolabs.cloud/",
            "comment": "Source rows are normalized from v2 `results` or compatible source arrays.",
        },
    },
    "perplexity": {
        "domains": {
            "source": "https://docs.perplexity.ai/docs/search/quickstart",
            "comment": (
                "`search_domain_filter` on Search API and Sonar (allowlist or `-domain` denylist)."
            ),
        },
        "country": {
            "source": "https://docs.perplexity.ai/docs/sonar/quickstart",
            "comment": (
                "Search API has no `gl` country param; Sonar supports regional bias via search options."
            ),
        },
        "language": {
            "source": "https://docs.perplexity.ai/api-reference/search-post",
            "comment": (
                "`search_language_filter` on Search API (ISO 639-1). Not exposed on Sonar chat requests."
            ),
        },
        "answer": {
            "source": "https://docs.perplexity.ai/docs/sonar/quickstart",
            "comment": (
                "Sonar assistant message — synthesized prose with citations (`/chat/completions`). "
                "Search API returns raw `results[]` only (no LLM answer field)."
            ),
        },
        "content": {
            "source": "https://docs.perplexity.ai/api-reference/search-post",
            "comment": (
                "Search API: larger `snippet` via `snippet_mode`, `max_tokens`, `max_tokens_per_page`. "
                "Sonar does not return full page bodies."
            ),
        },
        "snippet": {
            "source": "https://docs.perplexity.ai/api-reference/search-post",
            "comment": (
                "Search API `results[].snippet`. Sonar has no ranked snippet list — use Search API or citations."
            ),
        },
    },
    "gemini": {
        "answer": {
            "source": "https://ai.google.dev/gemini-api/docs/google-search",
            "comment": (
                "Grounded model text in `candidates[0].content.parts`; request with `answer=true` "
                "to populate SearchResponse.answer."
            ),
        },
        "snippet": {
            "source": "https://ai.google.dev/gemini-api/docs/google-search",
            "comment": (
                "`groundingMetadata.groundingChunks[]` — each `web.uri` / `web.title` becomes a result row."
            ),
        },
    },
    "you": {
        "domains": {
            "source": "https://you.com/docs/search/overview",
            "comment": (
                "Search: `include_domains`, `exclude_domains`, `boost_domains` (up to 500). "
                "Research: `source_control` domain lists (beta)."
            ),
        },
        "country": {
            "source": "https://you.com/docs/search/overview",
            "comment": (
                "Search: `country` (ISO 3166-1 alpha-2). Research: `source_control.country`."
            ),
        },
        "date": {
            "source": "https://you.com/docs/research/overview",
            "comment": (
                "Research API `source_control.freshness` only. Search API has no date-range filter."
            ),
        },
        "answer": {
            "source": "https://you.com/docs/api-reference/research/v1-research",
            "comment": (
                "Research `output.content` — Markdown with citations. Search returns ranked snippets only."
            ),
        },
        "content": {
            "source": "https://you.com/docs/api-reference/research/v1-research",
            "comment": (
                "Research sources include URL, title, and excerpt text. Search has no full-page body field."
            ),
        },
        "snippet": {
            "source": "https://you.com/docs/api-reference/search/v1-search",
            "comment": (
                "Search: ranked web results with snippets. Research: source excerpts in `output.sources[]`."
            ),
        },
        "highlights": {
            "source": "https://you.com/docs/api-reference/search/v1-search",
            "comment": "Search API: multiple `snippets` strings per web result. Not on Research API.",
        },
    },
    "jina": {
        "content": {
            "source": "https://jina.ai/reader/",
            "comment": "Search returns markdown page bodies unless `X-Respond-With: no-content` is set.",
        },
    },
    "kagi": {
        "snippet": {
            "source": "https://help.kagi.com/kagi/api/search.html",
            "comment": "Each result includes a `snippet`; length follows account Search settings.",
        },
    },
    "firecrawl": {
        "country": {
            "source": "https://docs.firecrawl.dev/api-reference/endpoint/search",
            "comment": "`country` — ISO country code on POST /v2/search.",
        },
        "content": {
            "source": "https://docs.firecrawl.dev/features/search",
            "comment": "`scrapeOptions.formats` (e.g. `markdown`) embeds full page text per hit.",
        },
        "news": {
            "source": "https://docs.firecrawl.dev/api-reference/endpoint/search",
            "comment": "`sources: [{\"type\": \"news\"}]` for news results.",
        },
    },
    "google_pse": {
        "domains": {
            "source": "https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list",
            "comment": "Single `siteSearch` + `siteSearchFilter` (`i` include / `e` exclude)—first domain only.",
        },
        "country": {
            "source": "https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list",
            "comment": "`gl` — geolocation of end user.",
        },
        "language": {
            "source": "https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list",
            "comment": "`hl` UI language and `lr` lang_restrict.",
        },
        "date": {
            "source": "https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list",
            "comment": "`sort=date:r:YYYYMMDD:YYYYMMDD` when both range ends are set.",
        },
        "safe_search": {
            "source": "https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list",
            "comment": "`safe`: `active` or `off`.",
        },
    },
    "searxng": {
        "language": {
            "source": "https://docs.searxng.org/dev/search_api.html",
            "comment": "`language` query parameter (instance default if omitted).",
        },
        "safe_search": {
            "source": "https://docs.searxng.org/dev/search_api.html",
            "comment": "`safesearch` 0=off, 1=moderate, 2=strict.",
        },
        "answer": {
            "source": "https://docs.searxng.org/dev/search_api.html",
            "comment": "Instant answers in the `answers` array when engines provide them.",
        },
    },
    "duckduckgo": {
        "country": {
            "source": "https://pypi.org/project/ddgs/",
            "comment": "DDGS `region` / locale parameters (see package docs).",
        },
        "safe_search": {
            "source": "https://pypi.org/project/ddgs/",
            "comment": "DDGS `safesearch` mapping for web search.",
        },
    },
    "serper": {
        "country": {
            "source": "https://serper.dev/docs",
            "comment": "`gl` — country code on POST /search and /news.",
        },
        "language": {
            "source": "https://serper.dev/docs",
            "comment": "`hl` — interface language.",
        },
        "answer": {
            "source": "https://serper.dev/docs",
            "comment": "Answer box / knowledge graph surfaced in JSON when Google returns them.",
        },
        "news": {
            "source": "https://serper.dev/docs",
            "comment": "POST /news for news SERP.",
        },
    },
    "serpapi": {
        "country": {
            "source": "https://serpapi.com/search-api",
            "comment": "`gl` — country code.",
        },
        "language": {
            "source": "https://serpapi.com/search-api",
            "comment": "`hl` — language code.",
        },
        "safe_search": {
            "source": "https://serpapi.com/search-api",
            "comment": "`safe` — active or off.",
        },
        "answer": {
            "source": "https://serpapi.com/search-api",
            "comment": "Answer box fields when present in the engine JSON.",
        },
        "news": {
            "source": "https://serpapi.com/search-api",
            "comment": "`engine=google_news` (or other news engines).",
        },
    },
    "searchapi": {
        "country": {
            "source": "https://www.searchapi.io/docs/google",
            "comment": "`gl` parameter on Google engine requests.",
        },
        "language": {
            "source": "https://www.searchapi.io/docs/google",
            "comment": "`hl` — language of the SERP.",
        },
        "answer": {
            "source": "https://www.searchapi.io/docs/google",
            "comment": "Featured snippets / answer box when returned by the engine.",
        },
        "news": {
            "source": "https://www.searchapi.io/docs/google-news",
            "comment": "Use the Google News engine for news results.",
        },
    },
}

# Extra matrix columns: synthesis / research APIs (same API keys as base provider, different endpoint).
# Empty — multi-product providers are merged into base columns (see MODE_META / FEATURE_META).
AI_MATRIX_PRODUCTS: tuple[dict[str, str | list[str] | dict[str, tuple[str, str, str]]], ...] = ()

VIA_SUFFIX = " · "  # display suffix for multi-product columns (e.g. "Research · You.com")


def ai_matrix_display(product: str, brand: str) -> str:
    return f"{product}{VIA_SUFFIX}{brand}"


# Extra matrix columns: one per SerpApi `engine=` backend (replaces a single SerpApi column).
SERPAPI_MATRIX_ENGINES: tuple[dict[str, str], ...] = (
    {
        "engine": "google",
        "brand": "Google",
        "docs": "https://serpapi.com/search-api",
        "website": "https://www.google.com",
        "news_engine": "google_news",
    },
    {
        "engine": "bing",
        "brand": "Bing",
        "docs": "https://serpapi.com/bing-search-api",
        "website": "https://www.bing.com",
        "news_engine": "bing_news",
    },
    {
        "engine": "baidu",
        "brand": "Baidu",
        "docs": "https://serpapi.com/baidu-search-api",
        "website": "https://www.baidu.com",
        "news_engine": "baidu_news",
    },
    {
        "engine": "yandex",
        "brand": "Yandex",
        "docs": "https://serpapi.com/yandex-search-api",
        "website": "https://yandex.com",
        "news_engine": "",
    },
    {
        "engine": "duckduckgo",
        "brand": "DuckDuckGo",
        "docs": "https://serpapi.com/duckduckgo-search-api",
        "website": "https://duckduckgo.com",
        "news_engine": "duckduckgo_news",
    },
    {
        "engine": "yahoo",
        "brand": "Yahoo",
        "docs": "https://serpapi.com/yahoo-search-api",
        "website": "https://www.yahoo.com",
        "news_engine": "yahoo",
    },
)


def serpapi_matrix_slug(engine: str) -> str:
    return f"serpapi_{engine}"


def serpapi_matrix_display(brand: str) -> str:
    return f"{brand} · SerpApi"


PARTIAL_NOTES: dict[str, dict[str, str]] = {
    "serper": {
        "answer": "Answer only when the SERP includes an answer box (not explicitly requested).",
    },
    "serpapi": {
        "answer": "Answer only when the SERP includes an answer box (not explicitly requested).",
    },
    "searchapi": {
        "answer": "Answer only when the SERP includes an answer box (not explicitly requested).",
    },
    "google_pse": {
        "domains": "Single include or exclude domain via siteSearch (first list item).",
        "date": "Date range via sort=date:r:start:end (Custom Search JSON API).",
    },
    "searxng": {
        "answer": "Returns instant-answer text from the answers field when available.",
    },
}


def _register_serpapi_matrix_meta() -> None:
    """Populate FEATURE_META / PARTIAL_NOTES for serpapi_<engine> matrix slugs."""
    for entry in SERPAPI_MATRIX_ENGINES:
        slug = serpapi_matrix_slug(entry["engine"])
        docs = entry["docs"]
        engine = entry["engine"]
        news = entry.get("news_engine") or ""
        locale: dict[str, dict[str, str]] = {}
        if engine == "google":
            locale = {
                "country": {"source": docs, "comment": "`gl` — country code on `engine=google`."},
                "language": {"source": docs, "comment": "`hl` — language code."},
                "safe_search": {"source": docs, "comment": "`safe`: `active` or `off`."},
            }
        elif engine == "bing":
            locale = {
                "country": {"source": docs, "comment": "`cc` — country code on `engine=bing`."},
                "language": {"source": docs, "comment": "`setlang` — UI/search language."},
                "safe_search": {
                    "source": docs,
                    "comment": "`safe_search`: off, moderate, strict.",
                },
            }
        elif engine == "duckduckgo":
            locale = {
                "country": {
                    "source": docs,
                    "comment": "`kl` region tag (e.g. us-en) combines country + language.",
                },
                "language": {"source": docs, "comment": "Set via `kl` (e.g. us-en, uk-en)."},
                "safe_search": {"source": docs, "comment": "`safe_search` on DuckDuckGo engine."},
            }
        elif engine == "yandex":
            locale = {
                "country": {"source": docs, "comment": "`lr` — Yandex region id when supported."},
                "language": {
                    "source": docs,
                    "comment": "Language via Yandex-specific params (see SerpApi docs).",
                },
            }
        elif engine == "baidu":
            locale = {
                "language": {
                    "source": docs,
                    "comment": "Language filter via Baidu-specific params (`ct`, etc.).",
                },
            }
        elif engine == "yahoo":
            locale = {
                "safe_search": {"source": docs, "comment": "`safe_search` on Yahoo engine."},
            }

        FEATURE_META[slug] = {
            "snippet": {
                "source": docs,
                "comment": f"Organic results via SerpApi `engine={engine}`.",
            },
            "answer": {
                "source": docs,
                "comment": "Answer box when the engine JSON includes one (not explicitly requested).",
            },
            "news": {
                "source": docs,
                "comment": (
                    f"`search_type=news` → `engine={news}` on SerpApi."
                    if news
                    else "News via SerpApi where a dedicated news engine exists for this backend."
                ),
            },
            **locale,
        }
        PARTIAL_NOTES[slug] = {
            "answer": "Answer only when the SERP includes an answer box (not explicitly requested).",
        }


def _register_ai_matrix_meta() -> None:
    for entry in AI_MATRIX_PRODUCTS:
        slug = str(entry["slug"])
        MODE_META[slug] = {
            "values": list(entry["modes"]),  # type: ignore[arg-type]
            "source": str(entry["mode_source"]),
            "comment": str(entry["mode_comment"]),
        }
        feats: dict[str, dict[str, str]] = {}
        for key, triple in (entry.get("features") or {}).items():
            sup, source, comment = triple  # type: ignore[misc]
            feats[key] = {"source": source, "comment": comment}
            SUPPORT_OVERRIDE.setdefault(slug, {})[key] = sup
        if feats:
            FEATURE_META[slug] = feats


_register_ai_matrix_meta()
_register_serpapi_matrix_meta()


def links_for(slug: str) -> dict[str, str]:
    for entry in AI_MATRIX_PRODUCTS:
        if entry["slug"] == slug:
            return {"docs": str(entry["docs"]), "website": str(entry["website"])}
    if slug.startswith("serpapi_"):
        engine = slug.removeprefix("serpapi_")
        for entry in SERPAPI_MATRIX_ENGINES:
            if entry["engine"] == engine:
                return {"docs": entry["docs"], "website": entry["website"]}
    return LINKS.get(slug, {})


def mode_for(slug: str, docs: str, website: str, *, engine: str | None = None) -> dict:
    for entry in AI_MATRIX_PRODUCTS:
        if entry["slug"] == slug:
            return {
                "values": list(entry["modes"]),  # type: ignore[arg-type]
                "source_url": str(entry["mode_source"]),
                "comment": str(entry["mode_comment"]),
            }
    if engine:
        return {
            "values": ["balanced"],
            "source_url": docs or website,
            "comment": (
                f"Fixed SerpApi backend `engine={engine}` (set via anysearch `engine=\"{engine}\"` "
                f"with `provider=\"serpapi\"`). No separate fast/deep tier on this engine."
            ),
        }
    meta = MODE_META.get(slug)
    if meta:
        return {
            "values": meta["values"],
            "source_url": meta["source"],
            "comment": meta["comment"],
        }
    fallback = docs or website
    return {
        "values": ["balanced"],
        "source_url": fallback,
        "comment": "Standard search tier (no separate fast/deep API parameter documented).",
    }


def feature_entry(
    slug: str,
    key: str,
    support: str,
    docs: str,
    website: str,
    default_comment: str,
) -> dict:
    custom = FEATURE_META.get(slug, {}).get(key)
    if custom:
        return feat(support, custom["source"], custom["comment"])
    partial = PARTIAL_NOTES.get(slug, {}).get(key)
    comment = partial or default_comment
    return feat(support, docs or website, comment)


def feat(support: str, source_url: str, comment: str) -> dict:
    return {"support": support, "source_url": source_url, "comment": comment}


def string_val(value: str, source_url: str, comment: str) -> dict:
    return {"value": value, "source_url": source_url, "comment": comment}


def list_val(values: list[str], source_url: str, comment: str) -> dict:
    return {"values": values, "source_url": source_url, "comment": comment}
