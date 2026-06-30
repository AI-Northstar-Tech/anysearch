# anysearch (JavaScript / TypeScript)

**One interface for every web search API.** `anysearch` is an adapter layer — think
LiteLLM, but for search providers — that lets you call Exa, Parallel, Brave, Tavily,
SerpAPI, Perplexity, Linkup, Firecrawl, and more through a single function with a
common set of parameters and a common response shape. It also ships a dependency-free
**stdio MCP server** that adapts to whatever API keys you have configured.

```ts
import { search, AnySearch } from "anysearch";

// Auto-selects a provider based on which API keys are set in your environment.
const resp = await search("best vector databases 2026", { maxResults: 5 });
for (const r of resp.results) console.log(r.title, r.url);

// Pin a provider and ask for richer content — same parameters everywhere.
const exa = await search("how do transformers work", {
  provider: "exa",
  includeContent: true,
  highlights: true,
  includeSummary: true,
});
```

## Install

Install the latest version from GitHub **`main`** (not on npm yet):

```bash
npm install github:dhruv-anand-aintech/anysearch#main:js
```

The package is REST-based (uses the built-in `fetch`), so it has **no runtime
dependencies** and every provider works out of the box. Provider SDKs are optional and
only needed for the `native()` escape hatch:

```bash
npm install exa-js          # then: await native("exa")
npm install @tavily/core    # then: await native("tavily")
```

## Providers

`exa`, `parallel`, `tavily`, `brave`, `keiro`, `linkup`, `perplexity`, `serper`, `serpapi`,
`searchapi`, `you`, `jina`, `kagi`, `firecrawl`, `google_pse`, `searxng`, `duckduckgo`
(keyless fallback). Each reads its API key from the environment — see the
[root README](../README.md) for the full env-var table.

## Unified parameters (`SearchParams`)

`query` is the first argument; everything else goes in the options object:

| Param | Type | Notes |
| --- | --- | --- |
| `provider` | `string` | omit to auto-select |
| `maxResults` | `number` | honored everywhere |
| `searchType` | `"web" \| "news"` | |
| `engine` | `string` | SerpApi only: `google`, `bing`, `baidu`, `yandex`, `duckduckgo`, … |
| `country` / `language` | `string` | ISO codes |
| `includeDomains` / `excludeDomains` | `string[]` | |
| `startPublishedDate` / `endPublishedDate` | `string` | ISO 8601 |
| `safeSearch` | `"off" \| "moderate" \| "strict"` | |
| `mode` | `"fast" \| "balanced" \| "deep"` | depth knob, mapped per provider |
| `answer` | `boolean` | synthesized answer where supported |
| `includeContent` | `boolean` | full page text where supported |
| `includeSummary` | `boolean` | per-result AI summary where supported |
| `highlights` | `boolean` | relevant excerpts where supported |
| `extra` | `object` | raw provider-specific passthrough |
| `fallbacks` | `string[]` | providers to try if the primary fails |
| `onUnsupported` | `"warn" \| "ignore" \| "error"` | default `"warn"` |

### Response shape (`SearchResponse`)

```ts
resp.provider;        // "exa"
resp.answer;          // synthesized answer, if any
resp.results;         // SearchResult[]

const r = resp.results[0];
r.title; r.url; r.snippet; r.text; r.summary; r.highlights; r.score;
r.publishedDate; r.author; r.source; r.raw;
```

## Client, fallbacks, async, native escape hatch

```ts
import { AnySearch, native } from "anysearch";

const client = new AnySearch({ provider: "exa", fallbacks: ["tavily", "brave"] });
const resp = await client.search("...", { mode: "deep" });

// Drop down to a provider's official SDK (must be installed separately)
const exa = await native("exa"); // -> new Exa({ apiKey })
```

## MCP server

```bash
npx anysearch-mcp           # stdio MCP server
npx anysearch-mcp --probe   # also verify each provider with a tiny live query
```

Tools: `search`, `list_providers`, `check_providers`, `migrate_codebase`.

## Build from source

```bash
npm install
npm run build      # tsc -> dist/
npm test           # node --test (mocked fetch)
```
