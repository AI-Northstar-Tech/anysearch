#!/usr/bin/env python3
"""Generate search_matrix/data/*.json from the anysearch Python provider registry."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON_SRC = ROOT / "python" / "src"
sys.path.insert(0, str(PYTHON_SRC))
sys.path.insert(0, str(ROOT / "scripts"))

from anysearch.client import AnySearch  # noqa: E402

from search_matrix_provider_meta import (  # noqa: E402
    AI_MATRIX_PRODUCTS,
    ENV_SOURCES,
    EXTRA_SOURCES,
    FEATURE_META,
    MATRIX_NOTES,
    PARTIAL_NOTES,
    PRICING_META,
    FREE_TIER_META,
    SERPAPI_MATRIX_ENGINES,
    SUPPORT_OVERRIDE,
    ai_matrix_display,
    feat,
    feature_entry,
    links_for,
    list_val,
    mode_for,
    serpapi_matrix_display,
    serpapi_matrix_slug,
    string_val,
)

DATA_DIR = ROOT / "docs" / "tools" / "search_matrix" / "data"
GITHUB_REPO = "https://github.com/dhruv-anand-aintech/anysearch"

DISPLAY_NAMES = {
    "gemini": "Gemini",
    "google_pse": "Google PSE",
    "duckduckgo": "DuckDuckGo",
    "searxng": "SearXNG",
    "serpapi": "SerpApi",
}

FEATURE_KEYS = [
    "domains",
    "country",
    "language",
    "date",
    "safe_search",
    "answer",
    "content",
    "summary",
    "highlights",
    "news",
]

FEATURE_LABELS = {
    "domains": "Domain filters",
    "country": "Country (gl)",
    "language": "Language",
    "date": "Published date range",
    "safe_search": "Safe search",
    "answer": "AI answer",
    "content": "Full page text",
    "summary": "AI per-result summary",
    "highlights": "Query highlights",
    "news": "News search type",
}


def build_provider(row: dict, *, slug: str | None = None, display: str | None = None) -> dict:
    name = row["name"]
    slug = slug or name
    caps = set(row["capabilities"])
    links_meta = links_for(slug)
    docs = links_meta.get("docs", row.get("config_hint", ""))
    website = links_meta.get("website", "")
    display = display or DISPLAY_NAMES.get(slug, name.replace("_", " ").title())
    env_source = ENV_SOURCES.get(
        "serpapi" if slug.startswith("serpapi_") else slug, docs or website
    )
    extra_pkg = row.get("extra_package") or ""
    if extra_pkg:
        extra_source = EXTRA_SOURCES.get(slug, docs or website)
        extra_value = extra_pkg
        extra_comment = f"Optional PyPI package: {extra_pkg} (install via anysearch-sdk extra `{slug}`)."
    else:
        extra_source = docs or website
        extra_value = "— (REST only)"
        extra_comment = "HTTP API only; no required vendor Python SDK."

    partial_notes = PARTIAL_NOTES.get(slug, {})
    overrides = SUPPORT_OVERRIDE.get(slug, {})

    def support_for(key: str) -> str:
        if key in overrides:
            return overrides[key]
        if key in caps:
            return "full"
        if key in partial_notes:
            return "partial"
        if key == "answer" and (
            slug in ("serper", "serpapi", "searchapi") or slug.startswith("serpapi_")
        ):
            return "partial"
        if key == "domains" and slug == "google_pse":
            return "partial"
        if key == "answer" and slug == "searxng":
            return "partial"
        return "none"

    out: dict = {
        "name": display,
        "links": {
            "docs": docs,
            "github": GITHUB_REPO,
            "website": website,
            "slug": slug,
        },
        "env_keys": string_val(
            ", ".join(row["env_keys"]) if row["env_keys"] else "(none — keyless)",
            env_source,
            "API keys and configuration variables documented by the provider.",
        ),
        "python_extra": string_val(extra_value, extra_source, extra_comment),
        "requires_key": feat(
            "none" if not row["requires_key"] else "full",
            env_source,
            "No API key required."
            if not row["requires_key"]
            else "Valid API key required for every request.",
        ),
        "snippet": feat(
            "full",
            FEATURE_META.get(slug, {}).get("snippet", {}).get("source", docs or website),
            FEATURE_META.get(slug, {}).get("snippet", {}).get(
                "comment",
                "Short description field returned with each result.",
            ),
        ),
    }

    for key in FEATURE_KEYS:
        sup = support_for(key)
        default_comment = FEATURE_LABELS.get(key, key)
        out[key] = feature_entry(slug, key, sup, docs, website, default_comment)

    engine_hint = slug.removeprefix("serpapi_") if slug.startswith("serpapi_") else None
    mode = mode_for(slug, docs, website, engine=engine_hint)
    out["mode"] = list_val(mode["values"], mode["source_url"], mode["comment"])
    pricing = PRICING_META.get(slug)
    if pricing is None and slug.startswith("serpapi_"):
        pricing = PRICING_META.get("serpapi")
    if pricing is None:
        pricing = {
            "value": "Pricing not published as a fixed per-query API rate.",
            "source_url": docs or website,
            "comment": "No mode-specific per-1K search price was available in public docs.",
        }
    out["pricing_per_1k"] = string_val(
        pricing["value"],
        pricing["source_url"],
        pricing["comment"],
    )
    free_tier = FREE_TIER_META.get(slug)
    if free_tier is None and slug.startswith("serpapi_"):
        free_tier = FREE_TIER_META.get("serpapi")
    if free_tier is None:
        free_tier = {
            "value": "No public free API allowance documented.",
            "source_url": docs or website,
            "comment": "Provider documentation does not publish a standing free request or credit allowance.",
        }
    out["free_tier_limits"] = string_val(
        free_tier["value"],
        free_tier["source_url"],
        free_tier["comment"],
    )

    notes = []
    if not row["requires_key"]:
        notes.append("No API key required (keyless fallback).")
    if extra_pkg:
        notes.append(f"Native SDK package: {extra_pkg}.")
    if slug in MATRIX_NOTES:
        notes.append(MATRIX_NOTES[slug])
    out["notes"] = " ".join(notes)

    return out


def build_serpapi_matrix_provider(row: dict, entry: dict[str, str]) -> dict:
    """One matrix column per SerpApi engine backend."""
    engine = entry["engine"]
    slug = serpapi_matrix_slug(engine)
    display = serpapi_matrix_display(entry["brand"])
    docs = entry["docs"]
    website = entry["website"]
    payload = build_provider(row, slug=slug, display=display)
    payload["links"] = {
        "docs": docs,
        "github": GITHUB_REPO,
        "website": website,
        "slug": slug,
    }
    payload["env_keys"] = string_val(
        "SERPAPI_API_KEY, SERPAPI_KEY",
        ENV_SOURCES["serpapi"],
        f"Same SerpApi key for all engines; anysearch uses `engine=\"{engine}\"`.",
    )
    payload["python_extra"] = string_val(
        row.get("extra_package") or "google-search-results",
        EXTRA_SOURCES["serpapi"],
        f"pip extra `serpapi`; call with `provider=\"serpapi\"`, `engine=\"{engine}\"`.",
    )
    payload["notes"] = (
        f"SerpApi proxy to {entry['brand']} (`engine={engine}`). "
        + (payload.get("notes") or "")
    ).strip()
    return payload


def build_ai_matrix_provider(base_row: dict, entry: dict) -> dict:
    """Matrix column for a synthesis/research API that shares credentials with a base provider."""
    slug = str(entry["slug"])
    base = str(entry["base"])
    display = ai_matrix_display(str(entry["product"]), str(entry["brand"]))
    docs = str(entry["docs"])
    website = str(entry["website"])
    env_source = ENV_SOURCES.get(base, docs)
    extra_pkg = base_row.get("extra_package") or ""
    if extra_pkg:
        extra_source = EXTRA_SOURCES.get(base, docs)
        extra_value = extra_pkg
        extra_comment = (
            f"Optional PyPI package via anysearch extra `{base}` (vendor SDK exposes this API)."
        )
    else:
        extra_source = docs
        extra_value = "— (REST only)"
        extra_comment = "HTTP API only; no required vendor Python SDK."

    overrides = SUPPORT_OVERRIDE.get(slug, {})

    def support_for(key: str) -> str:
        if key in overrides:
            return overrides[key]
        return "none"

    out: dict = {
        "name": display,
        "links": {
            "docs": docs,
            "github": GITHUB_REPO,
            "website": website,
            "slug": slug,
        },
        "env_keys": string_val(
            ", ".join(base_row["env_keys"]) if base_row["env_keys"] else "(none)",
            env_source,
            f"Same credentials as {display.split(' · ')[-1]} Search (`{', '.join(base_row['env_keys'])}`).",
        ),
        "python_extra": string_val(extra_value, extra_source, extra_comment),
        "requires_key": feat(
            "none" if not base_row["requires_key"] else "full",
            env_source,
            "Valid API key required for every request.",
        ),
        "snippet": feat(
            support_for("snippet"),
            FEATURE_META.get(slug, {}).get("snippet", {}).get("source", docs),
            FEATURE_META.get(slug, {}).get("snippet", {}).get(
                "comment",
                "Short description field returned with each result.",
            ),
        ),
    }

    for key in FEATURE_KEYS:
        sup = support_for(key)
        default_comment = FEATURE_LABELS.get(key, key)
        out[key] = feature_entry(slug, key, sup, docs, website, default_comment)

    mode = mode_for(slug, docs, website)
    out["mode"] = list_val(mode["values"], mode["source_url"], mode["comment"])
    pricing = PRICING_META.get(slug) or {
        "value": "Pricing not published as a fixed per-query API rate.",
        "source_url": docs,
        "comment": "No mode-specific per-1K search price was available in public docs.",
    }
    out["pricing_per_1k"] = string_val(
        pricing["value"],
        pricing["source_url"],
        pricing["comment"],
    )
    free_tier = FREE_TIER_META.get(slug) or {
        "value": "No public free API allowance documented.",
        "source_url": docs,
        "comment": "Provider documentation does not publish a standing free request or credit allowance.",
    }
    out["free_tier_limits"] = string_val(
        free_tier["value"],
        free_tier["source_url"],
        free_tier["comment"],
    )
    note = str(entry.get("notes") or "")
    endpoint = entry.get("endpoint")
    if endpoint:
        note = f"{endpoint}. {note}".strip()
    out["notes"] = note
    return out


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for p in DATA_DIR.glob("*.json"):
        p.unlink()

    info = AnySearch().provider_info()
    serpapi_row = next((r for r in info if r["name"] == "serpapi"), None)
    written = 0
    for row in sorted(info, key=lambda r: r["name"]):
        if row["name"] == "serpapi":
            if not serpapi_row:
                continue
            for entry in SERPAPI_MATRIX_ENGINES:
                payload = build_serpapi_matrix_provider(serpapi_row, entry)
                fname = f"{serpapi_matrix_slug(entry['engine'])}.json"
                path = DATA_DIR / fname
                path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
                print("wrote", path.name)
                written += 1
            continue
        payload = build_provider(row)
        path = DATA_DIR / f"{row['name']}.json"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print("wrote", path.name)
        written += 1

    by_name = {r["name"]: r for r in info}
    for entry in AI_MATRIX_PRODUCTS:
        base = str(entry["base"])
        base_row = by_name.get(base)
        if not base_row:
            print("skip", entry["slug"], "(missing base", base + ")")
            continue
        payload = build_ai_matrix_provider(base_row, entry)
        fname = f"{entry['slug']}.json"
        path = DATA_DIR / fname
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print("wrote", path.name)
        written += 1

    print(f"Generated {written} provider files in {DATA_DIR}")


if __name__ == "__main__":
    main()
