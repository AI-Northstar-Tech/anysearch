import type { HttpResponse } from "../http.js";
import type { SearchRequest, SearchResponse } from "../types.js";
import { finalize, result, type ProviderContext, type ProviderSpec } from "./base.js";

const MODE: Record<string, string> = { fast: "light", balanced: "ai", deep: "deep" };

function firstString(...values: unknown[]): string | undefined {
  for (const value of values) {
    if (typeof value === "string" && value) return value;
  }
  return undefined;
}

function sourceItems(data: any): any[] {
  if (Array.isArray(data?.results)) return data.results;
  if (Array.isArray(data?.sources)) return data.sources;
  if (Array.isArray(data?.citations)) return data.citations;
  if (Array.isArray(data?.answer?.sources)) return data.answer.sources;
  if (Array.isArray(data?.data?.results)) return data.data.results;
  if (Array.isArray(data?.data?.sources)) return data.data.sources;
  return [];
}

function answerText(data: any): string | undefined {
  return firstString(data?.answer, data?.answer?.text, data?.answer?.content, data?.data?.answer);
}

function endpointFor(req: SearchRequest): string {
  if (req.includeContent) return "/api/v2/search/content";
  if (req.mode) return "/api/v2/search/fast";
  return "/api/v2/keirolabs";
}

export const keiro: ProviderSpec = {
  name: "keiro",
  envKeys: ["KEIRO_API_KEY"],
  baseUrlEnv: ["KEIRO_BASE_URL"],
  defaultBaseUrl: "https://kierolabs.space",
  capabilities: new Set(["mode", "content"]),

  prepare(ctx: ProviderContext, req: SearchRequest) {
    const endpoint = endpointFor(req);
    const body: Record<string, unknown> = {
      apiKey: ctx.apiKey,
      query: req.query,
      maxResults: req.maxResults,
    };
    if (endpoint !== "/api/v2/keirolabs") {
      body.mode = MODE[req.mode ?? ""] ?? "ai";
    }
    Object.assign(body, req.extra);
    return {
      method: "POST",
      url: `${ctx.baseUrl}${endpoint}`,
      headers: { "Content-Type": "application/json" },
      json: body,
    };
  },

  parse(_ctx, res: HttpResponse, req: SearchRequest, elapsedMs: number): SearchResponse {
    const data = res.data ?? {};
    const results = sourceItems(data).map((item: any) => {
      const snippet = firstString(item.snippet, item.description, item.content, item.text);
      return result({
        title: firstString(item.title, item.name),
        url: firstString(item.url, item.link, item.source_url),
        snippet,
        text: req.includeContent ? firstString(item.full_text, item.text, item.content, item.raw_content) : undefined,
        score: typeof item.score === "number" ? item.score : undefined,
        publishedDate: firstString(item.published_date, item.publishedDate, item.date),
        raw: item,
      });
    });
    return finalize(keiro, req, results, data, {
      answer: answerText(data),
      totalResults: data.total_results ?? data.totalResults,
      requestId: firstString(data.request_id, data.requestId, data.id),
      elapsedMs,
    });
  },
};
