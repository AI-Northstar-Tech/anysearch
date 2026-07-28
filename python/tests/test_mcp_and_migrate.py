"""Tests for the migration scanner and the stdio MCP server plumbing."""

from __future__ import annotations

import json
from anysearch.mcp.migrate import scan_codebase
from anysearch.mcp.server import Server


def _write(path, content):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def test_scan_codebase_detects_providers(tmp_path):
    _write(tmp_path / "a.py", "from exa_py import Exa\nclient = Exa(api_key='x')\n")
    _write(tmp_path / "b.js", "const r = await fetch('https://api.tavily.com/search')\n")
    _write(tmp_path / "c.py", "import requests\nrequests.get('https://serpapi.com/search')\n")
    (tmp_path / "node_modules").mkdir()
    _write(tmp_path / "node_modules" / "ignored.js", "https://api.exa.ai/search")

    report = scan_codebase(root=str(tmp_path))
    detected = set(report["providers_detected"])
    assert {"exa", "tavily", "serpapi"} <= detected
    # node_modules is skipped
    assert all("node_modules" not in f["file"] for f in report["findings"])
    assert report["total_findings"] >= 3
    assert any("anysearch.search" in f["suggestion"] for f in report["findings"])


def test_scan_codebase_filter_providers(tmp_path):
    _write(tmp_path / "a.py", "from exa_py import Exa\nfrom tavily import TavilyClient\n")
    report = scan_codebase(root=str(tmp_path), providers=["exa"])
    assert report["providers_detected"] == ["exa"]


def test_mcp_initialize_and_tools_list():
    server = Server(probe=False)
    init = server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                          "params": {"protocolVersion": "2025-06-18"}})
    assert init["result"]["serverInfo"]["name"] == "anysearch"
    assert init["result"]["protocolVersion"] == "2025-06-18"

    # notifications return nothing
    assert server.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None

    listed = server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tool_names = {t["name"] for t in listed["result"]["tools"]}
    assert {"search", "list_providers", "check_providers", "migrate_codebase"} == tool_names


def test_mcp_list_providers_tool():
    server = Server(probe=False)
    resp = server.handle({
        "jsonrpc": "2.0", "id": 3, "method": "tools/call",
        "params": {"name": "list_providers", "arguments": {}},
    })
    payload = json.loads(resp["result"]["content"][0]["text"])
    assert "duckduckgo" in payload["configured"]
    assert len(payload["providers"]) >= 14


def test_mcp_migrate_tool(tmp_path):
    with open(tmp_path / "x.py", "w") as fh:
        fh.write("from tavily import TavilyClient\n")
    server = Server(probe=False)
    resp = server.handle({
        "jsonrpc": "2.0", "id": 4, "method": "tools/call",
        "params": {"name": "migrate_codebase", "arguments": {"path": str(tmp_path)}},
    })
    assert resp["result"]["isError"] is False
    payload = resp["result"]["structuredContent"]
    assert "tavily" in payload["providers_detected"]


def test_mcp_unknown_method():
    server = Server(probe=False)
    resp = server.handle({"jsonrpc": "2.0", "id": 9, "method": "does/not/exist"})
    assert resp["error"]["code"] == -32601
