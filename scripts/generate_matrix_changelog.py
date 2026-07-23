#!/usr/bin/env python3
"""Backfill a compact, cell-linked matrix changelog from Git history."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
IGNORED_KEYS = {"name", "links", "notes", "deprecated"}


def git(*args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if check and result.returncode:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def git_json(revision: str, path: str) -> dict[str, Any] | None:
    raw = git("show", f"{revision}:{path}", check=False)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def short(value: Any, limit: int = 72) -> str:
    if isinstance(value, list):
        text = ", ".join(str(item) for item in value)
    else:
        text = str(value)
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def semantic_value(cell: Any) -> tuple[str, Any] | None:
    if not isinstance(cell, dict):
        return ("value", cell)
    if "support" in cell:
        return ("support", cell["support"])
    if "values" in cell:
        return ("values", cell["values"])
    if "value" in cell:
        return ("value", cell["value"])
    return None


def support_summary(name: str, label: str, support: str) -> str:
    wording = {
        "full": "now supported",
        "partial": "now partially supported",
        "none": "now marked unsupported",
        "unknown": "now marked unknown",
        "": "support cleared",
    }.get(support, f"set to {support}")
    return f"{name}: {label} {wording}"


def change_summary(name: str, label: str, before: Any, after: Any) -> str:
    old_semantic = semantic_value(before)
    new_semantic = semantic_value(after)
    if new_semantic and new_semantic != old_semantic:
        kind, value = new_semantic
        if kind == "support":
            return support_summary(name, label, str(value))
        return f"{name}: {label} updated to {short(value)}"
    return f"{name}: {label} evidence refreshed"


def load_current(data_dir: Path) -> dict[str, dict[str, Any]]:
    return {
        path.relative_to(ROOT).as_posix(): json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(data_dir.glob("*.json"))
    }


def labels_from_schema(schema_path: Path) -> dict[str, str]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    labels: dict[str, str] = {}
    for key, spec in schema.get("properties", {}).items():
        parts = [part.strip() for part in spec.get("$comment", "").split("|")]
        labels[key] = parts[1] if len(parts) > 1 and parts[1] else key.replace("_", " ").title()
    return labels


def first_cell_key(row: dict[str, Any]) -> str | None:
    for preferred in ("form_factor", "latest_major_update", "requires_key", "pricing_per_1k"):
        if preferred in row:
            return preferred
    return next((key for key in row if key not in IGNORED_KEYS), None)


def item_for(
    current_row: dict[str, Any],
    key: str,
    summary: str,
) -> dict[str, str]:
    row_slug = current_row.get("links", {}).get("slug") or slug(current_row.get("name", "item"))
    return {"summary": summary, "target": f"cell-{slug(row_slug)}-{slug(key)}"}


def changes_for_pair(
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
    current_row: dict[str, Any],
    labels: dict[str, str],
) -> list[dict[str, str]]:
    if after is None:
        return []
    name = str(after.get("name") or current_row.get("name") or "Provider")
    if before is None:
        key = first_cell_key(current_row)
        return [item_for(current_row, key, f"{name} added to the comparison")] if key else []

    items: list[dict[str, str]] = []
    for key in sorted(set(before) | set(after)):
        if key in IGNORED_KEYS or before.get(key) == after.get(key) or key not in current_row:
            continue
        if key not in after:
            continue
        label = labels.get(key, key.replace("_", " ").title())
        items.append(
            item_for(
                current_row,
                key,
                change_summary(name, label, before.get(key), after.get(key)),
            )
        )
    return items


def dedupe(items: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[tuple[str, str]] = set()
    result: list[dict[str, str]] = []
    for item in items:
        marker = (item["summary"], item["target"])
        if marker not in seen:
            seen.add(marker)
            result.append(item)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix-dir", required=True)
    args = parser.parse_args()

    matrix_dir = ROOT / args.matrix_dir
    data_dir = matrix_dir / "data"
    data_rel = data_dir.relative_to(ROOT).as_posix()
    current = load_current(data_dir)
    labels = labels_from_schema(matrix_dir / "schema.json")
    entries: list[dict[str, Any]] = []

    history = git(
        "log",
        "--reverse",
        "--format=%H%x09%cs%x09%s",
        "--",
        data_rel,
    ).splitlines()
    for line in history:
        commit, commit_date, title = line.split("\t", 2)
        changed_paths = git(
            "diff-tree",
            "--root",
            "--no-commit-id",
            "--name-only",
            "-r",
            commit,
            "--",
            data_rel,
        ).splitlines()
        items: list[dict[str, str]] = []
        for path in changed_paths:
            current_row = current.get(path)
            if current_row is None:
                continue
            before = git_json(f"{commit}^", path)
            after = git_json(commit, path)
            items.extend(changes_for_pair(before, after, current_row, labels))
        items = dedupe(items)
        if items:
            entries.append(
                {"date": commit_date, "commit": commit[:7], "title": title, "items": items}
            )

    dirty_paths = git("diff", "--name-only", "HEAD", "--", data_rel).splitlines()
    dirty_items: list[dict[str, str]] = []
    for path in dirty_paths:
        current_row = current.get(path)
        if current_row is None:
            continue
        before = git_json("HEAD", path)
        dirty_items.extend(changes_for_pair(before, current_row, current_row, labels))
    dirty_items = dedupe(dirty_items)
    if dirty_items:
        entries.append(
            {
                "date": date.today().isoformat(),
                "commit": "",
                "title": "Unreleased matrix update",
                "items": dirty_items,
            }
        )

    entries.reverse()
    output = {
        "entry_count": sum(len(entry["items"]) for entry in entries),
        "entries": entries,
    }
    (matrix_dir / "changelog.json").write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"matrix changelog: {output['entry_count']} cell-linked changes")


if __name__ == "__main__":
    main()
