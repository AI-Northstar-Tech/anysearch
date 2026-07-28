/** Provider registry: name/alias -> spec, plus selection priority. */

import { ProviderNotFoundError } from "../errors.js";
import type { ProviderSpec } from "./base.js";
import { brave } from "./brave.js";
import { duckduckgo } from "./duckduckgo.js";
import { exa } from "./exa.js";
import { firecrawl } from "./firecrawl.js";
import { gemini } from "./gemini.js";
import { googlePse } from "./googlePse.js";
import { jina } from "./jina.js";
import { kagi } from "./kagi.js";
import { keiro } from "./keiro.js";
import { linkup } from "./linkup.js";
import { octen } from "./octen.js";
import { parallel } from "./parallel.js";
import { perplexity } from "./perplexity.js";
import { searchapi } from "./searchapi.js";
import { searxng } from "./searxng.js";
import { serpapi } from "./serpapi.js";
import { serper } from "./serper.js";
import { tavily } from "./tavily.js";
import { you } from "./you.js";

// Auto-selection order; keyless DuckDuckGo fallback last so it works out of the box.
export const PROVIDER_SPECS: ProviderSpec[] = [
  octen,
  exa,
  parallel,
  tavily,
  brave,
  keiro,
  linkup,
  perplexity,
  gemini,
  serper,
  serpapi,
  searchapi,
  you,
  jina,
  kagi,
  firecrawl,
  googlePse,
  searxng,
  duckduckgo,
];

export const DEFAULT_PRIORITY: string[] = PROVIDER_SPECS.map((s) => s.name);

const REGISTRY = new Map<string, ProviderSpec>();
for (const spec of PROVIDER_SPECS) {
  REGISTRY.set(spec.name, spec);
  for (const alias of spec.aliases ?? []) REGISTRY.set(alias, spec);
}

export function getProviderSpec(name: string): ProviderSpec {
  const key = (name ?? "").trim().toLowerCase().replace(/-/g, "_");
  const spec = REGISTRY.get(key);
  if (!spec) throw new ProviderNotFoundError(name, listProviderNames());
  return spec;
}

export function listProviderNames(): string[] {
  return PROVIDER_SPECS.map((s) => s.name);
}

export type { ProviderSpec } from "./base.js";
