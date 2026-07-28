import type { HttpResponse } from "../http.js";
import type { SearchRequest, SearchResponse } from "../types.js";
import { finalize, result, type ProviderContext, type ProviderSpec } from "./base.js";

export const octen: ProviderSpec = {
  name: "octen",
  aliases: ["octen_ai"],
  envKeys: ["OCTEN_API_KEY"],
  defaultBaseUrl: "https://api.octen.ai",
  capabilities: new Set([
    "domains", "language", "date", "safe_search", "content", "highlights", "news",
  ]),

  prepare(ctx: ProviderContext, req: SearchRequest) {
    const body: Record<string, unknown> = {
      query: req.query,
      count: req.maxResults,
      topic: req.searchType === "news" ? "news" : "general",
    };
    if (req.includeDomains.length) body.include_domains = req.includeDomains;
    if (req.excludeDomains.length) body.exclude_domains = req.excludeDomains;
    if (req.language) body.language = [req.language.toLowerCase()];
    if (req.startPublishedDate || req.endPublishedDate) body.time_basis = "published";
    if (req.startPublishedDate) body.start_time = req.startPublishedDate;
    if (req.endPublishedDate) body.end_time = req.endPublishedDate;
    if (req.safeSearch) body.safesearch = req.safeSearch === "off" ? "off" : "strict";
    if (req.highlights) body.highlight = { enable: true };
    if (req.includeContent) body.full_content = { enable: true };
    Object.assign(body, req.extra);
    return {
      method: "POST",
      url: `${ctx.baseUrl}/search`,
      headers: { "x-api-key": ctx.apiKey ?? "", "Content-Type": "application/json" },
      json: body,
    };
  },

  parse(_ctx, res: HttpResponse, req: SearchRequest, elapsedMs: number): SearchResponse {
    const payload = res.data ?? {};
    const data = payload.data ?? {};
    const results = (data.results ?? []).map((item: any) => {
      const highlights = item.highlight ? [item.highlight] : [];
      return result({
        title: item.title,
        url: item.url,
        snippet: item.highlight,
        text: item.full_content,
        highlights,
        publishedDate: item.time_published,
        author: item.authors,
        raw: item,
      });
    });
    const providerLatency = Number(payload.meta?.latency);
    return finalize(octen, req, results, payload, {
      requestId: payload.request_id,
      elapsedMs: Number.isFinite(providerLatency) ? providerLatency : elapsedMs,
    });
  },
};
