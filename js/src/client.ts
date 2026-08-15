/** Public API: the `AnySearch` client plus module-level helpers. */

import { ConfigurationError, isRecoverable, MissingAPIKeyError } from "./errors.js";
import { send } from "./http.js";
import {
  baseUrlFromEnv,
  configHint,
  isConfigured,
  keyFromEnv,
  type ProviderContext,
  type ProviderSpec,
} from "./providers/base.js";
import { getProviderSpec, listProviderNames } from "./providers/index.js";
import { availableProviders, enforceCapabilities, selectProvider } from "./router.js";
import { makeRequest, type Env, type SearchParams, type SearchRequest, type SearchResponse } from "./types.js";

const UNIFIED_FIELDS = [
  "maxResults", "searchType", "engine", "country", "language", "includeDomains", "excludeDomains",
  "startPublishedDate", "endPublishedDate", "safeSearch", "mode", "answer",
  "includeContent", "includeSummary", "highlights",
] as const;

export interface AnySearchOptions {
  provider?: string;
  apiKey?: string;
  baseUrl?: string;
  fallbacks?: string[];
  onUnsupported?: "ignore" | "warn" | "error";
  timeoutMs?: number;
  priority?: string[];
  providerConfig?: Record<string, Record<string, unknown>>;
  env?: Env;
}

export interface ProviderInfo {
  name: string;
  aliases: string[];
  configured: boolean;
  requiresKey: boolean;
  envKeys: string[];
  capabilities: string[];
  extraPackage?: string;
  configHint: string;
}

export class AnySearch {
  readonly provider?: string;
  readonly apiKey?: string;
  readonly baseUrl?: string;
  readonly fallbacks: string[];
  readonly onUnsupported: "ignore" | "warn" | "error";
  readonly timeoutMs: number;
  readonly priority?: string[];
  readonly providerConfig: Record<string, Record<string, unknown>>;
  private readonly env: Env;

  constructor(opts: AnySearchOptions = {}) {
    this.provider = opts.provider;
    this.apiKey = opts.apiKey;
    this.baseUrl = opts.baseUrl;
    this.fallbacks = opts.fallbacks ?? [];
    this.onUnsupported = opts.onUnsupported ?? "warn";
    this.timeoutMs = opts.timeoutMs ?? 30000;
    this.priority = opts.priority;
    this.providerConfig = opts.providerConfig ?? {};
    this.env = opts.env ?? (process.env as Env);
  }

  // -- introspection ---------------------------------------------------------

  providers(): string[] {
    return availableProviders(this.env);
  }

  static allProviders(): string[] {
    return listProviderNames();
  }

  providerInfo(): ProviderInfo[] {
    return listProviderNames().map((name) => {
      const spec = getProviderSpec(name);
      return {
        name: spec.name,
        aliases: spec.aliases ?? [],
        configured: isConfigured(spec, this.env),
        requiresKey: spec.requiresKey !== false,
        envKeys: spec.envKeys ?? [],
        capabilities: [...spec.capabilities].sort(),
        extraPackage: spec.extraPackage,
        configHint: configHint(spec),
      };
    });
  }

  /** Dynamically import a provider's official SDK (requires it to be installed). */
  async native(provider?: string): Promise<unknown> {
    const name = provider ?? this.provider ?? selectProvider(this.env, this.priority);
    const spec = getProviderSpec(name);
    if (!spec.nativeImport) {
      throw new ConfigurationError(`Provider '${spec.name}' has no official SDK; it is REST-only.`);
    }
    let mod: Record<string, unknown>;
    try {
      mod = (await import(spec.nativeImport.module)) as Record<string, unknown>;
    } catch (err) {
      throw new ConfigurationError(
        `Native SDK for '${spec.name}' is not installed. Install anysearch from GitHub (npm install github:dhruv-anand-aintech/anysearch#main:js), then: npm install ${spec.nativeImport.module}`,
      );
    }
    const ctx = this.context(spec);
    for (const exportName of spec.nativeImport.exports) {
      const candidate = mod[exportName];
      if (typeof candidate === "function") {
        try {
          return new (candidate as new (opts: unknown) => unknown)({ apiKey: ctx.apiKey });
        } catch {
          try {
            return (candidate as (opts: unknown) => unknown)({ apiKey: ctx.apiKey });
          } catch {
            /* try next export */
          }
        }
      }
    }
    throw new ConfigurationError(`Could not construct a native client for '${spec.name}'.`);
  }

  // -- internals -------------------------------------------------------------

  private context(spec: ProviderSpec, requestProvider?: string, apiKeyOverride?: string, baseUrlOverride?: string): ProviderContext {
    const configuredProvider = requestProvider ?? this.provider;
    const isNamed = configuredProvider != null && getProviderSpec(configuredProvider).name === spec.name;
    const apiKey = (isNamed ? apiKeyOverride ?? this.apiKey : undefined) ?? keyFromEnv(spec, this.env);
    const baseUrl = (
      (isNamed ? baseUrlOverride ?? this.baseUrl : undefined) ??
      baseUrlFromEnv(spec, this.env) ??
      spec.defaultBaseUrl ??
      ""
    ).replace(/\/+$/, "");
    return { apiKey, baseUrl, env: this.env, config: this.providerConfig[spec.name] ?? {} };
  }

  private requireConfigured(spec: ProviderSpec, ctx: ProviderContext): void {
    if (spec.requiresKey !== false && !ctx.apiKey) {
      throw new MissingAPIKeyError(spec.name, configHint(spec));
    }
    if (spec.requiresBaseUrl && !ctx.baseUrl) {
      throw new ConfigurationError(`Provider '${spec.name}' requires a base URL. ${configHint(spec)}`);
    }
  }

  private buildRequest(spec: ProviderSpec, query: string, params: SearchParams): SearchRequest {
    const providerParams = params.providerParams?.[spec.name] ?? {};
    const extra = { ...providerParams, ...(params.extra ?? {}) };
    const partial = { extra } as unknown as Record<string, unknown>;
    const src = params as unknown as Record<string, unknown>;
    for (const field of UNIFIED_FIELDS) {
      if (src[field] !== undefined) partial[field] = src[field];
    }
    return makeRequest(query, partial as Partial<SearchRequest>);
  }

  private chain(primary: string, overrideFallbacks?: string[]): string[] {
    const fallbacks = overrideFallbacks ?? this.fallbacks;
    const seen = new Set([getProviderSpec(primary).name]);
    const chain = [primary];
    for (const fb of fallbacks) {
      const canonical = getProviderSpec(fb).name;
      if (!seen.has(canonical)) {
        seen.add(canonical);
        chain.push(fb);
      }
    }
    return chain;
  }

  async search(query: string, params: SearchParams = {}): Promise<SearchResponse> {
    const provider = params.provider ?? this.provider;
    const onUnsupported = params.onUnsupported ?? this.onUnsupported;
    const timeoutMs = params.timeoutMs ?? this.timeoutMs;
    const primary = provider ?? selectProvider(this.env, this.priority);
    const chain = this.chain(primary, params.fallbacks);

    let lastError: unknown;
    for (const name of chain) {
      const spec = getProviderSpec(name);
      const ctx = this.context(spec, provider, params.apiKey, params.baseUrl);
      try {
        this.requireConfigured(spec, ctx);
        const req = enforceCapabilities(spec, this.buildRequest(spec, query, params), onUnsupported);
        const prepared = spec.prepare(ctx, req);
        const start = performance.now();
        const res = await send(spec.name, prepared, timeoutMs);
        return spec.parse(ctx, res, req, performance.now() - start);
      } catch (err) {
        if (isRecoverable(err)) {
          lastError = err;
          continue;
        }
        throw err;
      }
    }
    throw lastError;
  }
}

const defaultClient = new AnySearch();

export function search(query: string, params: SearchParams = {}): Promise<SearchResponse> {
  return defaultClient.search(query, params);
}

export function listProviders(configuredOnly = false): string[] {
  return configuredOnly ? availableProviders(process.env as Env) : listProviderNames();
}

export function providerInfo(): ProviderInfo[] {
  return defaultClient.providerInfo();
}

export function native(provider?: string): Promise<unknown> {
  return defaultClient.native(provider);
}
